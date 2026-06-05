import re

from allauth.socialaccount.forms import SignupForm
from django import forms
from django.contrib.auth import get_user_model


class AutoSocialSignupForm(SignupForm):
    """Hide social signup fields while still passing valid account data to allauth."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        email = self.initial.get("email") or getattr(self.sociallogin.user, "email", "")
        username = self.initial.get("username") or getattr(self.sociallogin.user, "username", "")

        if not username:
            username = self._make_unique_username(email)

        self.initial["email"] = email
        self.initial["username"] = username

        if "email" in self.fields:
            self.fields["email"].initial = email
            self.fields["email"].widget = forms.HiddenInput()

        if "username" in self.fields:
            self.fields["username"].initial = username
            self.fields["username"].widget = forms.HiddenInput()

    def _make_unique_username(self, email):
        User = get_user_model()
        base = email.split("@", 1)[0] if email else "google_user"
        base = re.sub(r"[^A-Za-z0-9_]+", "", base).strip("_").lower() or "google_user"
        base = base[:120]

        username = base
        suffix = 1
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base}{suffix}"

        return username
