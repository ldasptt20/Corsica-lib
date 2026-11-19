import os
from pathlib import Path
from urllib.parse import urlsplit

BASE = Path(__file__).resolve().parent.parent
PRIVATE = Path(os.getenv("MEMBERS_DATA_DIR") or BASE / ".private")
PRIVATE.mkdir(mode=0o700, exist_ok=True)
SECRET_KEY = os.environ["SESSION_SECRET"]
ORIGIN = (os.getenv("APP_BASE_URL") or os.getenv("RENDER_EXTERNAL_URL") or "http://127.0.0.1:8000").rstrip("/")
url = urlsplit(ORIGIN)
local = url.hostname in {"127.0.0.1", "localhost", "[::1]"}
if url.scheme != "https" and not (local and url.scheme == "http"):
    raise ValueError("HTTPS requis")
DEBUG = False
ALLOWED_HOSTS = [url.hostname]
ROOT_URLCONF = "members.urls"
INSTALLED_APPS = ["django.contrib.auth", "django.contrib.contenttypes", "django.contrib.sessions", "members"]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
TEMPLATES = [{"BACKEND": "django.template.backends.django.DjangoTemplates", "APP_DIRS": True,
              "OPTIONS": {"context_processors": ["django.template.context_processors.request"]}}]
DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": PRIVATE / "members.sqlite3",
                        "OPTIONS": {"transaction_mode": "IMMEDIATE", "timeout": 10}}}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
PASSWORD_HASHERS = ["django.contrib.auth.hashers.Argon2PasswordHasher"]
SESSION_COOKIE_SECURE = CSRF_COOKIE_SECURE = url.scheme == "https"
if os.getenv("RENDER") == "true":
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not local
SECURE_REFERRER_POLICY = "no-referrer"
SESSION_COOKIE_AGE = 86400
LOGIN_URL = "/connexion/"
LANGUAGE_CODE = "fr"
TIME_ZONE = "Europe/Paris"
USE_TZ = True
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("SMTP_HOST", "localhost")
EMAIL_PORT = int(os.getenv("SMTP_PORT", "587"))
EMAIL_USE_TLS = True
EMAIL_TIMEOUT = 8
EMAIL_HOST_USER = os.getenv("SMTP_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD", "")
DEFAULT_FROM_EMAIL = os.getenv("MAIL_FROM", "corsica@localhost")
YOTI_KEY = os.getenv("YOTI_API_KEY", "")
YOTI_SDK = os.getenv("YOTI_SDK_ID", "")
