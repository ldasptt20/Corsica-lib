from django.urls import path
from django.views.decorators.cache import never_cache
from django.views.generic import RedirectView

from . import views

urlpatterns = [path("", RedirectView.as_view(pattern_name="account"))]
for route, view, name in [
    ("inscription/", views.signup, "signup"), ("connexion/", views.signin, "signin"),
    ("deconnexion/", views.signout, "signout"), ("compte/", views.account, "account"),
    ("confirmation/renvoyer/", views.resend, "resend"), ("confirmation/<str:token>/", views.confirm, "confirm"),
    ("majorite/", views.start_age, "start_age"), ("majorite/retour/", views.age_return, "age_return"),
    ("rencontres/", views.discover, "discover"),
    ("profil/", views.edit, "edit"), ("photos/", views.upload, "upload"), ("photos/<int:pk>/", views.photo, "photo"),
]:
    urlpatterns.append(path(route, never_cache(view), name=name))
