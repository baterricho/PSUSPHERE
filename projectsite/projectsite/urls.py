from django.contrib import admin
from django.conf import settings
from django.urls import include, path
from django.shortcuts import redirect, render

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("studentorg.urls")),
    path("", include("pwa.urls")),
]

if settings.ALLAUTH_ENABLED:
    from allauth.socialaccount.models import SocialApp
    from allauth.socialaccount.providers.google.views import (
        oauth2_callback as google_oauth2_callback,
        oauth2_login as google_oauth2_login,
    )
    from allauth.socialaccount.providers.github.views import (
        oauth2_callback as github_oauth2_callback,
        oauth2_login as github_oauth2_login,
    )
    from allauth.socialaccount.views import signup as social_signup

    def social_unavailable(request, provider="social", status_code=503):
        return render(
            request,
            "socialaccount/unavailable.html",
            {"provider": provider.title()},
            status=status_code,
        )

    def google_login_entry(request, *args, **kwargs):
        try:
            return google_oauth2_login(request, *args, **kwargs)
        except SocialApp.DoesNotExist:
            return social_unavailable(request, provider="google", status_code=503)

    def google_callback_entry(request, *args, **kwargs):
        if "code" not in request.GET and "error" not in request.GET:
            return redirect("/accounts/google/login/")
        try:
            return google_oauth2_callback(request, *args, **kwargs)
        except SocialApp.DoesNotExist:
            return social_unavailable(request, provider="google", status_code=503)

    def github_login_entry(request, *args, **kwargs):
        try:
            return github_oauth2_login(request, *args, **kwargs)
        except SocialApp.DoesNotExist:
            return social_unavailable(request, provider="github", status_code=503)

    def github_callback_entry(request, *args, **kwargs):
        if "code" not in request.GET and "error" not in request.GET:
            return redirect("/accounts/github/login/")
        try:
            return github_oauth2_callback(request, *args, **kwargs)
        except SocialApp.DoesNotExist:
            return social_unavailable(request, provider="github", status_code=503)

    def social_signup_entry(request, *args, **kwargs):
        try:
            return social_signup(request, *args, **kwargs)
        except Exception:
            return redirect("/accounts/login/")

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("accounts/google/login/", google_login_entry),
        path("accounts/google/login/callback/", google_callback_entry),
        path("accounts/github/login/", github_login_entry),
        path("accounts/github/login/callback/", github_callback_entry),
        path("accounts/3rdparty/signup/", social_signup_entry),
        path("accounts/", include("allauth.urls")),
        path("", include("studentorg.urls")),
        path("", include("pwa.urls")),
    ]
else:
    def social_unavailable(request):
        return render(request, "socialaccount/unavailable.html", status=503)

    urlpatterns = [
        path("admin/", admin.site.urls),
        path("accounts/google/login/callback/", social_unavailable),
        path("accounts/google/login/", social_unavailable),
        path("accounts/github/login/callback/", social_unavailable),
        path("accounts/github/login/", social_unavailable),
        path("accounts/login/", social_unavailable),
        path("", include("studentorg.urls")),
        path("", include("pwa.urls")),
    ]
