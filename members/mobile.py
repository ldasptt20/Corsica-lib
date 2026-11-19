from functools import wraps

from django.db.models import Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET, require_POST

from . import forms, views
from .models import Favorite, Message, Profile


def fail(message, status):
    return JsonResponse({"error": message}, status=status)


def public(p):
    return {"id": p.pk, "pseudo": p.pseudo, "city": p.city, "kind": p.kind, "bio": p.bio}


def state(request):
    data = {"csrf": get_token(request), "connected": request.user.is_authenticated}
    if request.user.is_authenticated:
        p = request.user.profile
        data.update(profile=public(p), email_ok=p.email_ok, adult=bool(p.adult_at),
                    notice=request.session.pop("notice", ""))
    return JsonResponse(data)


def authenticated(view):
    @wraps(view)
    def check(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return fail("Connectez-vous à votre compte.", 401)
        return view(request, *args, **kwargs)
    return check


def verified(view):
    @authenticated
    @wraps(view)
    def check(request, *args, **kwargs):
        p = request.user.profile
        if not p.email_ok or not p.adult_at:
            return fail("Confirmez votre adresse et votre majorité.", 403)
        return view(request, p, *args, **kwargs)
    return check


@require_POST
def account_action(request, action):
    actions = {"signup": views.signup, "login": views.signin, "logout": views.signout,
               "resend": views.resend, "age": views.start_age}
    if action not in actions:
        return fail("Action inconnue.", 404)
    if action not in ("signup", "login") and not request.user.is_authenticated:
        return fail("Connectez-vous à votre compte.", 401)
    response = actions[action](request)
    if response.status_code == 429:
        return fail("Trop de tentatives. Réessayez dans 15 minutes.", 429)
    if action == "age":
        location = response.get("Location", "")
        if location.startswith("https://age.yoti.com/"):
            return JsonResponse({"url": location})
        return fail("Vérification Yoti indisponible pour ce compte.", 503)
    if response.status_code != 302:
        if action == "signup":
            form = forms.SignupForm(request.POST)
            errors = " ".join(str(e) for group in form.errors.values() for e in group)
            return fail(errors or "Inscription impossible avec ces informations.", 400)
        return fail("Adresse ou mot de passe incorrect.", 400)
    return state(request)


@require_GET
@authenticated
def result(request):
    views.age_return(request)
    return state(request)


@require_POST
@verified
def profile(request, p):
    form = forms.ProfileForm(request.POST, instance=p)
    if not form.is_valid():
        return fail("Vérifiez les champs du profil.", 400)
    form.save()
    return state(request)


@require_GET
@verified
def directory(request, p):
    peers = Profile.objects.filter(user__is_active=True, email_ok=True, adult_at__isnull=False).exclude(pk=p.pk)
    favorites = set(p.favorites.values_list("target_id", flat=True))
    return JsonResponse({"members": [dict(public(other), favorite=other.pk in favorites)
                                     for other in peers.order_by("pseudo", "pk")]})


@verified
def contact(request, p, pk, action):
    peer = Profile.objects.filter(pk=pk, user__is_active=True, email_ok=True, adult_at__isnull=False).exclude(pk=p.pk).first()
    if not peer:
        return fail("Profil indisponible.", 404)
    if action == "favorite" and request.method == "POST":
        if request.POST.get("enabled") == "true":
            Favorite.objects.get_or_create(owner=p, target=peer)
        else:
            Favorite.objects.filter(owner=p, target=peer).delete()
        return JsonResponse({"ok": True})
    if action == "messages" and request.method in ("GET", "POST"):
        if request.method == "POST":
            body = request.POST.get("body", "").strip()
            if not 1 <= len(body) <= 2000:
                return fail("Le message doit contenir de 1 à 2 000 caractères.", 400)
            if views.limited("message", p.pk, 100):
                return fail("Trop de messages. Réessayez plus tard.", 429)
            Message.objects.create(sender=p, recipient=peer, body=body)
        rows = Message.objects.filter(Q(sender=p, recipient=peer) | Q(sender=peer, recipient=p)).order_by("-pk")[:100]
        return JsonResponse({"messages": [{"mine": m.sender_id == p.pk, "body": m.body}
                                           for m in reversed(list(rows))]})
    return fail("Action indisponible.", 405)
