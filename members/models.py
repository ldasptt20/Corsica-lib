from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    TYPES = [("solo", "Solo"), ("couple", "Couple")]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    pseudo = models.CharField("Pseudonyme", max_length=40)
    city = models.CharField("Ville", max_length=80)
    kind = models.CharField("Type de profil", choices=TYPES, max_length=12)
    birth = models.DateField("Date de naissance")
    bio = models.CharField("Présentation", max_length=500, blank=True)
    email_ok = models.BooleanField(default=False)
    adult_at = models.DateTimeField(null=True)
    age_session = models.CharField(max_length=64, blank=True)
    age_ref = models.CharField(max_length=64, blank=True)
    age_until = models.DateTimeField(null=True)


class Photo(models.Model):
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE)
    jpeg = models.BinaryField()


class Attempt(models.Model):
    key = models.CharField(max_length=64, primary_key=True)
    expires = models.DateTimeField(db_index=True)
    count = models.PositiveIntegerField(default=0)
