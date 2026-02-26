from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.shortcuts import resolve_url
from django.utils import timezone
import logging
from .models import UserProfile


logger = logging.getLogger(__name__)


class AccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        explicit_next = (request.POST.get("next") or request.GET.get("next") or "").strip()
        if explicit_next:
            return explicit_next
        # Prefer session-preset redirect (set on signup)
        target = request.session.pop("_next_after_login", None) or request.session.pop(
            "post_login_redirect", None
        )
        if target:
            return target
        return super().get_login_redirect_url(request)

    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        # Ensure a profile exists and mark approval requested timestamp
        try:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            if not profile.requested_approval_at:
                profile.requested_approval_at = timezone.now()
                profile.save(update_fields=["requested_approval_at"])
        except Exception:
            logger.exception("Failed to initialize profile in account adapter", extra={"user_id": getattr(user, "id", None)})
        # After signup, keep intended destination if present; otherwise use profile
        try:
            explicit_next = (request.POST.get("next") or request.GET.get("next") or "").strip()
            session_next = request.session.get("_next_after_login") or request.session.get("post_login_redirect")
            if explicit_next:
                request.session["_next_after_login"] = explicit_next
            elif not session_next:
                request.session["post_login_redirect"] = resolve_url("user_profile")
        except Exception:
            logger.exception("Failed to store redirect intent in account adapter", extra={"user_id": getattr(user, "id", None)})
        return user


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # allauth handles auto-connection to existing accounts via email
        # (SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True)
        # Nothing to do here — just let allauth proceed.
        pass
