from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model
from allauth.account.signals import user_signed_up
from django.contrib.auth.signals import user_logged_in
from django.shortcuts import redirect
from django.utils import timezone
from .models import UserProfile, Review, ReviewReport, ActivityLog
from .utils import send_telegram_message

User = get_user_model()

@receiver(post_save, sender=User)
def create_profile_on_user_create(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(user_signed_up)
def handle_user_signed_up(request, user, **kwargs):
    # Ensure profile exists and mark pending approval
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.is_approved = False
    profile.requested_approval_at = timezone.now()
    profile.save(update_fields=["is_approved", "requested_approval_at"])
    # Auto-login is handled by allauth; set a flag in session to redirect
    request.session["post_login_redirect"] = "/profile/"

@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    # If not approved, direct to profile with a notice; else proceed
    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None
    # Determine redirect target
    target = request.session.pop("post_login_redirect", None)
    if not target:
        # If not approved, encourage completing profile/awaiting approval
        if profile and not profile.is_approved:
            target = "/profile/"
    if target:
        # Stash the target to be used by a custom middleware or view after login
        request.session["_next_after_login"] = target


@receiver(post_save, sender=Review)
def notify_new_review(sender, instance, created, **kwargs):
    if not created:
        return
    # Send to reviews group/channel if configured
    from django.conf import settings
    chat_ids = getattr(settings, 'TELEGRAM_REVIEWS_CHAT_IDS', [])
    if not chat_ids:
        return
    text = (
        f"<b>Yangi sharh</b>\n"
        f"Kompaniya: {instance.company.name}\n"
        f"Muallif: {instance.user_name}\n"
        f"Baho: {instance.rating}⭐\n"
        f"Matn: {instance.text[:300]}"
    )
    send_telegram_message(text, chat_ids=chat_ids)

    # Log creation
    try:
        ActivityLog.objects.create(
            actor=instance.user,  # may be null
            action='review_created',
            company=instance.company,
            review=instance,
            details=f"Review #{instance.pk} created by {instance.user_name} ({instance.rating}★)",
        )
    except Exception:
        pass


@receiver(pre_save, sender=Review)
def log_review_approval_change(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old = Review.objects.get(pk=instance.pk)
    except Review.DoesNotExist:
        return
    if not old.is_approved and instance.is_approved:
        # Approved now
        try:
            ActivityLog.objects.create(
                actor=getattr(instance, '_last_actor', None),  # optional pattern if set by views/admin
                action='review_approved',
                company=instance.company,
                review=instance,
                details=f"Review #{instance.pk} approved",
            )
        except Exception:
            pass


@receiver(post_save, sender=ReviewReport)
def log_review_reported(sender, instance, created, **kwargs):
    if not created:
        return
    try:
        ActivityLog.objects.create(
            actor=instance.reporter,
            action='review_reported',
            company=instance.review.company,
            review=instance.review,
            details=f"Report #{instance.pk} on Review #{instance.review_id} ({instance.reason})",
        )
    except Exception:
        pass
