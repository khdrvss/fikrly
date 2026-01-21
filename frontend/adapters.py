from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import resolve_url
from django.utils import timezone
from .models import UserProfile


class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        # Prefer session-preset redirect (set on signup)
        target = request.session.pop("_next_after_login", None) or request.session.pop(
            "post_login_redirect", None
        )
        if target:
            return target
        # If user is not approved yet, send to profile page
        user = request.user
        try:
            profile = user.profile
        except Exception:
            profile = None
        if profile is None:
            profile = UserProfile.objects.get_or_create(user=user)[0]
        if not profile.is_approved:
            return resolve_url("user_profile")
        return super().get_login_redirect_url(request)

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        # Ensure a profile exists and mark approval requested timestamp
        profile, _ = UserProfile.objects.get_or_create(user=user)
        if not profile.requested_approval_at:
            profile.requested_approval_at = timezone.now()
            profile.save(update_fields=["requested_approval_at"])
        # After signup, redirect them to profile to await approval
        request.session["post_login_redirect"] = resolve_url("user_profile")
        return user
