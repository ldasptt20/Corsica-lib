import io
from datetime import timedelta
from unittest.mock import patch
from uuid import uuid4

from django.core import mail, signing
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.utils import timezone
from PIL import Image

from .models import Photo, Profile


@override_settings(YOTI_SDK="test-sdk", EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class MemberFlow(TestCase):
    data = dict(pseudo="Maquis", city="Corte", kind="solo", birth="1994-09-09",
                email="Maquis@example.org", password="Un mot de passe long")

    def signup(self):
        self.client.post("/inscription/", self.data)
        return Profile.objects.get()

    def verify_email(self):
        link = mail.outbox[-1].body.splitlines()[-1].split(":8000")[-1]
        self.client.post(link)

    def test_signup_login_logout(self):
        p = self.signup()
        self.assertTrue(p.user.password.startswith("argon2"))
        self.assertEqual(p.user.email, self.data["email"].lower())
        self.assertRedirects(self.client.get("/profil/"), "/compte/")
        self.verify_email()
        self.assertRedirects(self.client.post("/photos/"), "/compte/")
        self.client.post("/deconnexion/")
        self.assertEqual(self.client.get("/compte/").status_code, 302)
        self.client.post("/connexion/", {**self.data, "password": "wrong"})
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertRedirects(self.client.post("/connexion/", self.data), "/compte/")

    def test_validation_and_duplicates(self):
        for changes in ({"birth": str(timezone.localdate())}, {"birth": "invalide"}, {"password": "abc"},
                        {"kind": "other"}, {"email": "wrong"}, {"city": ""}):
            self.client.post("/inscription/", {**self.data, **changes})
            self.assertFalse(Profile.objects.exists())
        self.signup()
        self.client.post("/deconnexion/")
        self.client.post("/inscription/", {**self.data, "email": self.data["email"].upper()})
        self.assertEqual(Profile.objects.count(), 1)

    def test_confirmation_bound_to_account_and_post(self):
        p = self.signup()
        url = mail.outbox[0].body.splitlines()[-1].split(":8000")[-1]
        self.client.get(url)
        self.client.post("/confirmation/tampered/")
        self.client.post("/confirmation/" + signing.dumps(p.user_id + 1, salt="verify-address") + "/")
        p.refresh_from_db()
        self.assertFalse(p.email_ok)
        self.client.post("/deconnexion/")
        self.client.post(url)
        self.assertRedirects(self.client.post("/connexion/", self.data), url)
        self.client.post(url)
        p.refresh_from_db()
        self.assertTrue(p.email_ok)

    def test_expiry_and_resend(self):
        self.signup()
        with patch("django.core.signing.time.time", return_value=1):
            expired = signing.dumps(Profile.objects.get().user_id, salt="verify-address")
        self.client.post("/confirmation/" + expired + "/")
        self.assertFalse(Profile.objects.get().email_ok)
        self.client.post("/confirmation/renvoyer/")
        self.verify_email()
        self.assertTrue(Profile.objects.get().email_ok)

    def test_csrf_and_login_limit(self):
        guarded = Client(enforce_csrf_checks=True)
        self.assertEqual(guarded.post("/inscription/", self.data).status_code, 403)
        for _ in range(12):
            self.client.post("/connexion/", self.data)
        self.assertEqual(self.client.post("/connexion/", self.data).status_code, 429)

    @patch("members.yoti.call")
    def test_age_and_profile(self, api):
        p = self.signup()
        self.client.post("/majorite/")
        api.assert_not_called()
        self.verify_email()
        session = str(uuid4())
        api.return_value = {"id": session}
        self.assertIn(session, self.client.post("/majorite/")["Location"])
        p.refresh_from_db()
        valid = dict(id=session, sdk_id="test-sdk", reference_id=p.age_ref, status="COMPLETE", type="OVER",
                     age=25, method="AGE_ESTIMATION", age_estimation=dict(level="PASSIVE", allowed=True, threshold=25))
        for wrong in (dict(id="other"), dict(reference_id="other"), dict(status="PENDING"),
                      dict(age=17), dict(method="MOBILE"), dict(sdk_id="other"), dict(type="UNDER")):
            api.return_value = {**valid, **wrong}
            self.client.get("/majorite/retour/?success=true")
            self.assertRedirects(self.client.get("/profil/"), "/compte/")
        api.return_value = valid
        self.client.get("/majorite/retour/")
        self.assertEqual(self.client.get("/profil/").status_code, 200)
        self.client.post("/profil/", {**self.data, "city": "Bastia", "bio": "Bonjour"})
        p.refresh_from_db()
        self.assertEqual(p.city, "Bastia")
        self.assertEqual(p.age_session, "")

    def test_no_provider_and_expired_session(self):
        p = self.signup()
        self.verify_email()
        with override_settings(YOTI_KEY=""):
            self.assertContains(self.client.post("/majorite/"), "indisponible")
        Profile.objects.filter(pk=p.pk).update(age_session=str(uuid4()), age_until=timezone.now()-timedelta(minutes=1))
        with patch("members.yoti.call") as api:
            self.client.get("/majorite/retour/")
            api.assert_not_called()
        self.assertFalse(Profile.objects.get().adult_at)

    def test_photos_private_and_reencoded(self):
        p = self.signup()
        Profile.objects.filter(pk=p.pk).update(email_ok=True, adult_at=timezone.now())
        raw = io.BytesIO()
        Image.new("RGB", (16, 16)).save(raw, format="PNG")
        self.client.post("/photos/", {"photo": SimpleUploadedFile("image.png", raw.getvalue())})
        photo = Photo.objects.get()
        url = f"/photos/{photo.pk}/"
        response = self.client.get(url)
        self.assertEqual(response["Content-Type"], "image/jpeg")
        self.assertIn("no-store", response["Cache-Control"])
        self.client.post("/photos/", {"photo": SimpleUploadedFile("bad.jpg", b"bad")})
        self.assertEqual(Photo.objects.count(), 1)
        self.client.post("/deconnexion/")
        self.assertEqual(self.client.get(url).status_code, 302)
        self.client.post("/inscription/", {**self.data, "email": "autre@example.org"})
        Profile.objects.exclude(pk=p.pk).update(email_ok=True, adult_at=timezone.now())
        self.assertEqual(self.client.get(url).status_code, 404)


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class MobileTests(TestCase):
    base = "/api/mobile/"

    def test_csrf_roundtrip(self):
        client = Client(enforce_csrf_checks=True)
        csrf = client.get(self.base + "state/").json()["csrf"]
        url = self.base + "account/signup/"
        self.assertEqual(client.post(url, MemberFlow.data).status_code, 403)
        state = client.post(url, MemberFlow.data, HTTP_X_CSRFTOKEN=csrf).json()
        self.assertTrue(state["connected"])
        self.assertFalse(state["adult"])
        self.assertEqual(client.get(self.base + "members/").status_code, 403)
        self.assertEqual(client.post(self.base + "account/logout/", HTTP_X_CSRFTOKEN=state["csrf"]).status_code, 200)
        self.assertEqual(client.get(self.base + "members/").status_code, 401)
        csrf = client.get(self.base + "state/").json()["csrf"]
        self.assertTrue(client.post(self.base + "account/login/", MemberFlow.data,
                                    HTTP_X_CSRFTOKEN=csrf).json()["connected"])

    def test_member_privacy_and_social(self):
        clients, profiles = [], []
        for n in range(3):
            client = Client()
            data = client.post(self.base + "account/signup/", {
                **MemberFlow.data, "email": f"test{n}@example.org", "pseudo": f"Compte{n}"}).json()
            clients.append(client)
            profiles.append(data["profile"]["id"])
        a, b, c = clients
        ida, idb, idc = profiles
        Profile.objects.filter(pk__in=[ida, idb]).update(adult_at=timezone.now(), email_ok=True)
        listing = a.get(self.base + "members/").json()["members"]
        self.assertEqual([p["id"] for p in listing], [idb])
        self.assertNotIn("email", listing[0])
        def url(pk, action):
            return self.base + f"members/{pk}/{action}/"
        fav = url(idb, "favorite")
        for _ in range(2):
            self.assertEqual(a.post(fav, {"enabled": "true"}).status_code, 200)
        self.assertTrue(a.get(self.base + "members/").json()["members"][0]["favorite"])
        a.post(fav, {"enabled": "false"})
        self.assertFalse(a.get(self.base + "members/").json()["members"][0]["favorite"])
        self.assertEqual(a.post(url(idc,"messages"), {"body": "Coucou"}).status_code, 404)
        self.assertEqual(a.post(url(idb,"messages"), {"body": " "}).status_code, 400)
        a.post(url(idb,"messages"), {"body": "Bonjour !"})
        self.assertEqual(b.get(url(ida,"messages")).json()["messages"], [{"mine": False,"body":"Bonjour !"}])
        self.assertEqual(c.get(url(ida,"messages")).status_code, 403)
        Profile.objects.filter(pk=idc).update(adult_at=timezone.now(), email_ok=True)
        self.assertEqual(c.get(url(ida,"messages")).json()["messages"], [])
        self.assertEqual(a.post(self.base + "profile/", {**MemberFlow.data, "city":"Ajaccio"}).json()["profile"]["city"], "Ajaccio")

    def test_member_block_and_report(self):
        first, second = Client(), Client()
        a = first.post(self.base + "account/signup/", {
            **MemberFlow.data, "email": "one@example.org", "pseudo": "Un"}).json()["profile"]["id"]
        b = second.post(self.base + "account/signup/", {
            **MemberFlow.data, "email": "two@example.org", "pseudo": "Deux"}).json()["profile"]["id"]
        Profile.objects.filter(pk__in=[a, b]).update(email_ok=True, adult_at=timezone.now())
        first.post(self.base + f"members/{b}/favorite/", {"enabled": "true"})
        self.assertEqual(first.post(self.base + f"members/{b}/report/", {"reason": "Profil suspect"}).status_code, 201)
        from .models import Block, Favorite, Report
        self.assertEqual(Report.objects.filter(reporter_id=a, target_id=b).count(), 1)
        self.assertEqual(first.post(self.base + f"members/{b}/block/", {"enabled": "true"}).status_code, 200)
        self.assertTrue(Block.objects.filter(owner_id=a, target_id=b).exists())
        self.assertFalse(Favorite.objects.filter(owner_id=a, target_id=b).exists())
        self.assertEqual(first.get(self.base + "members/").json()["members"], [])
        self.assertEqual(second.get(self.base + "members/").json()["members"], [])
        self.assertEqual(first.post(self.base + f"members/{b}/messages/", {"body": "Bonjour"}).status_code, 404)
        self.assertEqual(second.post(self.base + f"members/{a}/messages/", {"body": "Bonjour"}).status_code, 404)
        self.assertEqual(first.post(self.base + f"members/{b}/block/", {"enabled": "false"}).status_code, 200)
        self.assertEqual(len(first.get(self.base + "members/").json()["members"]), 1)
        self.assertEqual(first.post(self.base + f"members/{b}/report/", {"reason": "x"}).status_code, 400)
