import re

from allauth.socialaccount.forms import SignupForm
from django.contrib.auth import get_user_model


class AutoSocialSignupForm(SignupForm):
    """Continue social signup without asking for username or email again."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.clear()

    def save(self, request):
        user = self.sociallogin.user
        email = getattr(user, "email", "") or self.initial.get("email", "")

        if email and not user.email:
            user.email = email

        if not user.username:
            user.username = self._make_unique_username(email)

        user.set_unusable_password()
        self.sociallogin.save(request)
        return user

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
