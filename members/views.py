import io
import secrets
from datetime import timedelta
from functools import wraps
from smtplib import SMTPException

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core import signing
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.crypto import salted_hmac
from django.views.decorators.http import require_POST, require_safe, require_http_methods
from PIL import Image, ImageOps, UnidentifiedImageError

from . import yoti
from .forms import LoginForm, ProfileForm, SignupForm
from .models import Attempt, Photo, Profile


def page(request, title, **context):
    return render(request, "account.html", {"title": title, **context})


def limited(scope, identity, maximum):
    key = salted_hmac(scope, str(identity)).hexdigest()
    now = timezone.now()
    with transaction.atomic():
        Attempt.objects.filter(expires__lte=now).delete()
        item, _ = Attempt.objects.get_or_create(key=key, defaults={"expires": now + timedelta(minutes=15)})
        if item.count >= maximum:
            return True
        item.count += 1
        item.save(update_fields=["count"])
    return False


def wait(request):
    response = page(request, "Veuillez patienter", notice="Réessayez dans 15 minutes.")
    response.status_code = 429
    return response


def deliver(request):
    token = signing.dumps(request.user.pk, salt="verify-address")
    url = f"{settings.ORIGIN}/confirmation/{token}/"
    try:
        send_mail("Confirmez votre inscription à Corsica Lib",
                  f"Si vous avez créé ce compte, connectez-vous et confirmez votre adresse sous 24 heures.\n{url}",
                  settings.DEFAULT_FROM_EMAIL, [request.user.email])
    except (OSError, SMTPException):
        return "Envoi indisponible. Vous pouvez demander un nouveau lien depuis votre compte."
    return "Un lien de confirmation vous a été envoyé. Il est valable 24 heures."


@require_http_methods(["GET", "POST"])
def signup(request):
    if request.user.is_authenticated:
        return redirect("account")
    form = SignupForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and limited("signup", request.META.get("REMOTE_ADDR"), 10):
        return wait(request)
    if form.is_valid():
        email = form.cleaned_data["email"].lower()
        try:
            with transaction.atomic():
                user = User.objects.create_user(email, email, form.cleaned_data["password"])
                profile = form.save(commit=False)
                profile.user = user
                profile.save()
        except IntegrityError:
            form.add_error(None, "Inscription impossible avec ces informations. Essayez de vous connecter.")
        else:
            login(request, user)
            request.session["notice"] = deliver(request)
            return redirect("account")
    return page(request, "Créer mon compte", form=form, button="Créer mon compte")


@require_http_methods(["GET", "POST"])
def signin(request):
    form = LoginForm(request.POST if request.method == "POST" else None)
    if form.is_valid():
        email = form.cleaned_data["email"].lower()
        if limited("login-ip", request.META.get("REMOTE_ADDR"), 50) or limited("login-email", email, 12):
            return wait(request)
        user = authenticate(request, username=email, password=form.cleaned_data["password"])
        if user:
            login(request, user)
            token = request.session.pop("confirm_after_login", None)
            if token:
                return redirect("confirm", token=token)
            return redirect("account")
        form.add_error(None, "Adresse ou mot de passe incorrect.")
    return page(request, "Se connecter", form=form, button="Se connecter")


@require_POST
def signout(request):
    logout(request)
    return redirect("signin")


@login_required
def account(request):
    return page(request, "Mon compte", account=request.user.profile, notice=request.session.pop("notice", ""))


@login_required
@require_POST
def resend(request):
    if not request.user.profile.email_ok:
        if limited("resend", request.user.pk, 3):
            return wait(request)
        request.session["notice"] = deliver(request)
    return redirect("account")


@require_http_methods(["GET", "POST"])
def confirm(request, token):
    try:
        uid = signing.loads(token, salt="verify-address", max_age=86400)
    except signing.BadSignature:
        return page(request, "Lien expiré ou invalide", notice="Connectez-vous pour demander un nouveau lien.")
    if not request.user.is_authenticated:
        if request.method == "POST":
            request.session["confirm_after_login"] = token
            return redirect("signin")
        return page(request, "Confirmer mon adresse", button="Continuer avec mon compte")
    if uid != request.user.pk:
        return HttpResponseForbidden("Ce lien appartient à un autre compte.")
    if request.method == "POST":
        Profile.objects.filter(user_id=uid, email_ok=False).update(email_ok=True)
        return redirect("account")
    return page(request, "Confirmer mon adresse", button="Confirmer mon adresse")


@login_required
@require_POST
def start_age(request):
    profile = request.user.profile
    if not profile.email_ok or profile.adult_at:
        return redirect("account")
    if limited("age-start", profile.pk, 4):
        return wait(request)
    reference = secrets.token_hex(20)
    try:
        session, url = yoti.start(reference)
    except yoti.Unavailable:
        return page(request, "Vérification indisponible", notice="Le service de vérification de majorité est indisponible. Réessayez plus tard.")
    Profile.objects.filter(pk=profile.pk, adult_at=None).update(
        age_ref=reference, age_session=session, age_until=timezone.now() + timedelta(minutes=10))
    return redirect(url)


@login_required
@require_safe
def age_return(request):
    profile = request.user.profile
    if profile.adult_at or not profile.email_ok or not profile.age_session or profile.age_until <= timezone.now():
        return redirect("account")
    try:
        ok = yoti.passed(profile)
    except yoti.Unavailable:
        ok = False
    if ok:
        Profile.objects.filter(pk=profile.pk, age_session=profile.age_session, age_ref=profile.age_ref,
                               age_until__gt=timezone.now()).update(adult_at=timezone.now(), age_ref="", age_session="", age_until=None)
    else:
        request.session["notice"] = "Majorité non confirmée. Vous pouvez revérifier le résultat ou recommencer chez Yoti."
    return redirect("account")


def member(view):
    @login_required
    @wraps(view)
    def check(request, *args, **kwargs):
        profile = request.user.profile
        if not profile.email_ok or not profile.adult_at:
            return redirect("account")
        return view(request, profile, *args, **kwargs)
    return check


@member
@require_http_methods(["GET", "POST"])
def edit(request, profile):
    form = ProfileForm(request.POST if request.method == "POST" else None, instance=profile)
    if form.is_valid():
        form.save()
        return redirect("edit")
    return page(request, "Mon profil", form=form, button="Enregistrer", gallery=True,
                photos=Photo.objects.filter(owner=profile).values_list("pk", flat=True))


@member
@require_POST
def upload(request, profile):
    file = request.FILES.get("photo")
    if not file or file.size > 5 * 1024**2:
        return page(request, "Photo refusée", notice="Choisissez une image JPEG, PNG ou WebP de 5 Mo maximum.")
    try:
        with Image.open(file, formats=["JPEG", "PNG", "WEBP"]) as source:
            if source.width * source.height > 16_000_000:
                raise ValueError
            image = ImageOps.exif_transpose(source).convert("RGB")
            image.thumbnail((1400, 1400))
            image.info.clear()
            output = io.BytesIO()
            image.save(output, "JPEG", quality=85)
    except (ValueError, OSError, Image.DecompressionBombError, UnidentifiedImageError):
        return page(request, "Photo refusée", notice="Image illisible ou trop grande (16 mégapixels maximum).")
    with transaction.atomic():
        if Photo.objects.filter(owner=profile).count() >= 6:
            return page(request, "Album complet", notice="Vous pouvez conserver six photos sur votre profil.")
        Photo.objects.create(owner=profile, jpeg=output.getvalue())
    return redirect("edit")


@member
@require_safe
def photo(request, profile, pk):
    item = get_object_or_404(Photo, owner=profile, pk=pk)
    return HttpResponse(bytes(item.jpeg), content_type="image/jpeg")
