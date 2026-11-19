from django import forms
from django.utils import timezone

from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["pseudo", "city", "kind", "bio"]
        widgets = {"bio": forms.Textarea(attrs={"rows": 3})}


class SignupForm(forms.ModelForm):
    email = forms.EmailField(label="Adresse e-mail", max_length=150)
    password = forms.CharField(label="Mot de passe (12 caractères minimum)", strip=False,
                               min_length=12, max_length=128, widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}))

    class Meta:
        model = Profile
        fields = ["pseudo", "email", "password", "birth", "city", "kind"]
        widgets = {"birth": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d")}

    def clean_birth(self):
        birth = self.cleaned_data["birth"]
        today = timezone.localdate()
        age = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
        if age < 18 or age > 120:
            raise forms.ValidationError("Une date valide et un âge minimum de 18 ans sont requis.")
        return birth


class LoginForm(forms.Form):
    email = forms.EmailField(label="Adresse e-mail", max_length=150)
    password = forms.CharField(label="Mot de passe", strip=False, max_length=128,
                               widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}))
