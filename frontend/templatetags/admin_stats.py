from django import template
from django.contrib.auth import get_user_model
from frontend.models import Company, Review
from django.utils import timezone
from datetime import timedelta

register = template.Library()


@register.simple_tag
def admin_count_users():
    User = get_user_model()
    try:
        return User.objects.count()
    except Exception:
        return 0


@register.simple_tag
def admin_count_companies():
    try:
        return Company.objects.count()
    except Exception:
        return 0


@register.simple_tag
def admin_count_reviews():
    try:
        return Review.objects.count()
    except Exception:
        return 0


@register.simple_tag
def admin_count_pending_reviews():
    try:
        return Review.objects.filter(is_approved=False).count()
    except Exception:
        return 0


@register.simple_tag
def admin_users_recent_subtext(days=7):
    """Return a localized subtext like '3 aktiv (7 kun ichida)'."""
    User = get_user_model()
    try:
        since = timezone.now() - timedelta(days=int(days))
        count = User.objects.filter(last_login__gte=since).count()
        return f"{count} aktiv ({days} kun ichida)"
    except Exception:
        return "-"


@register.simple_tag
def admin_companies_verified_subtext():
    try:
        count = Company.objects.filter(is_verified=True).count()
        return f"{count} tasdiqlangan"
    except Exception:
        return "-"


@register.simple_tag
def admin_reviews_approved_subtext():
    try:
        count = Review.objects.filter(is_approved=True).count()
        return f"{count} tasdiqlangan"
    except Exception:
        return "-"


@register.simple_tag
def admin_pending_subtext():
    try:
        count = Review.objects.filter(is_approved=False).count()
        return f"{count} tasdiqlanmoqda"
    except Exception:
        return "-"
