from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save, post_delete
from django.contrib.auth import get_user_model
import logging
from allauth.account.signals import user_signed_up
from django.contrib.auth.signals import user_logged_in
from django.utils import timezone
from .models import (
    UserProfile,
    Review,
    ReviewReport,
    ActivityLog,
    Company,
    BusinessCategory,
    UserGamification,
    Badge,
    ReviewHelpfulVote,
    ReviewImage,
)
from .utils import send_telegram_message, send_telegram_review_notification
from .cache_utils import clear_public_cache

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_profile_on_user_create(sender, instance, created, **kwargs):
    if kwargs.get("raw", False):
        return
    if created:
        UserProfile.objects.get_or_create(user=instance)


@receiver(user_signed_up)
def handle_user_signed_up(request, user, **kwargs):
    # Ensure profile exists and auto-approve (reviews are moderated individually)
    try:
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.is_approved = True
        profile.approved_at = timezone.now()
        profile.requested_approval_at = timezone.now()
        profile.save(update_fields=["is_approved", "approved_at", "requested_approval_at"])
    except Exception:
        logger.exception("Failed to initialize user profile during signup", extra={"user_id": getattr(user, "id", None)})
    # Auto-login is handled by allauth; preserve explicit next target when present
    try:
        explicit_next = (request.POST.get("next") or request.GET.get("next") or "").strip()
        if explicit_next:
            request.session["_next_after_login"] = explicit_next
        elif not (
            request.session.get("_next_after_login")
            or request.session.get("post_login_redirect")
        ):
            request.session["post_login_redirect"] = "/profile/"
    except Exception:
        logger.exception("Failed to preserve redirect intent during signup", extra={"user_id": getattr(user, "id", None)})


@receiver(user_logged_in)
def handle_user_logged_in(sender, request, user, **kwargs):
    # Restore any intended redirect target set before login
    explicit_next = (request.POST.get("next") or request.GET.get("next") or "").strip()
    target = explicit_next or request.session.pop("_next_after_login", None) or request.session.pop(
        "post_login_redirect", None
    )
    if target:
        request.session["_next_after_login"] = target


@receiver(post_save, sender=Review)
def notify_new_review(sender, instance, created, **kwargs):
    if not created:
        return
    # Send notification with inline Approve / Reject buttons
    try:
        send_telegram_review_notification(instance)
    except Exception:
        pass

    # Log creation
    try:
        ActivityLog.objects.create(
            actor=instance.user,  # may be null
            action="review_created",
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
                actor=getattr(
                    instance, "_last_actor", None
                ),  # optional pattern if set by views/admin
                action="review_approved",
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
            action="review_reported",
            company=instance.review.company,
            review=instance.review,
            details=f"Report #{instance.pk} on Review #{instance.review_id} ({instance.reason})",
        )
    except Exception:
        pass


@receiver([post_save, post_delete], sender=Review)
def update_company_stats_signal(sender, instance, **kwargs):
    """
    Recalculate company stats whenever a review is saved (created/updated) or deleted.
    This ensures rating and review_count stay in sync.
    """
    from .utils import recalculate_company_stats

    if instance.company_id:
        recalculate_company_stats(instance.company_id)


@receiver([post_save, post_delete], sender=BusinessCategory)
def clear_cache_on_category_change(sender, instance, **kwargs):
    clear_public_cache()


@receiver([post_save, post_delete], sender=Company)
def clear_cache_on_company_change(sender, instance, **kwargs):
    update_fields = kwargs.get("update_fields")
    if update_fields and set(update_fields).issubset({"review_count", "rating"}):
        return
    clear_public_cache()


@receiver(pre_save, sender=Review)
def track_review_approval_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._old_is_approved = False
        return
    try:
        old = Review.objects.only("is_approved").get(pk=instance.pk)
        instance._old_is_approved = old.is_approved
    except Review.DoesNotExist:
        instance._old_is_approved = False


@receiver(post_save, sender=Review)
def clear_cache_on_approved_review_save(sender, instance, created, **kwargs):
    old_is_approved = getattr(instance, "_old_is_approved", False)
    if instance.is_approved or old_is_approved:
        clear_public_cache()


@receiver(post_delete, sender=Review)
def clear_cache_on_approved_review_delete(sender, instance, **kwargs):
    if instance.is_approved:
        clear_public_cache()


@receiver(pre_save, sender=Company)
def optimize_company_images(sender, instance, **kwargs):
    """
    Optimize company images before saving to reduce file size and improve load times.
    """
    if not instance.pk:
        # New company - optimize images if uploaded
        if instance.image:
            from .image_optimization import optimize_image

            optimized = optimize_image(
                instance.image, max_width=1200, max_height=800, quality=85
            )
            if optimized:
                instance.image = optimized

        if instance.logo:
            from .image_optimization import optimize_image

            optimized = optimize_image(
                instance.logo, max_width=400, max_height=400, quality=90
            )
            if optimized:
                instance.logo = optimized
    else:
        # Existing company - only optimize if image changed
        try:
            old_instance = Company.objects.get(pk=instance.pk)

            if instance.image and old_instance.image != instance.image:
                from .image_optimization import optimize_image

                optimized = optimize_image(
                    instance.image, max_width=1200, max_height=800, quality=85
                )
                if optimized:
                    instance.image = optimized

            if instance.logo and old_instance.logo != instance.logo:
                from .image_optimization import optimize_image

                optimized = optimize_image(
                    instance.logo, max_width=400, max_height=400, quality=90
                )
                if optimized:
                    instance.logo = optimized
        except Company.DoesNotExist:
            pass


@receiver(pre_save, sender=UserProfile)
def optimize_avatar(sender, instance, **kwargs):
    """
    Optimize user avatars before saving.
    """
    if instance.avatar:
        try:
            if instance.pk:
                old_instance = UserProfile.objects.get(pk=instance.pk)
                if old_instance.avatar != instance.avatar:
                    from .image_optimization import optimize_image

                    optimized = optimize_image(
                        instance.avatar, max_width=400, max_height=400, quality=90
                    )
                    if optimized:
                        instance.avatar = optimized
            else:
                from .image_optimization import optimize_image

                optimized = optimize_image(
                    instance.avatar, max_width=400, max_height=400, quality=90
                )
                if optimized:
                    instance.avatar = optimized
        except UserProfile.DoesNotExist:
            pass


# ============================================
# GAMIFICATION SIGNALS
# ============================================


@receiver(post_save, sender=User)
def create_gamification_profile(sender, instance, created, **kwargs):
    """Create gamification profile for new users"""
    if created and not kwargs.get("raw", False):
        UserGamification.objects.get_or_create(user=instance)


@receiver(post_save, sender=Review)
def update_gamification_on_review(sender, instance, created, **kwargs):
    """Update user's gamification stats when they post a review"""
    if not instance.user or kwargs.get("raw", False):
        return

    gamification, _ = UserGamification.objects.get_or_create(user=instance.user)

    if created and instance.is_approved:
        # New approved review
        gamification.total_reviews += 1
        gamification.add_xp(10, "Review posted")
        gamification.update_streak()

        # Check for unique companies reviewed
        unique_companies = (
            Review.objects.filter(user=instance.user, is_approved=True)
            .values("company")
            .distinct()
            .count()
        )
        gamification.companies_reviewed = unique_companies
        gamification.save()

        # Award badges
        if gamification.total_reviews == 1:
            Badge.objects.get_or_create(
                user=instance.user,
                badge_type="first_review",
                defaults={
                    "name": "Birinchi sharh",
                    "description": "Birinchi sharhingizni yozdingiz!",
                    "icon": "🎉",
                },
            )
        elif gamification.total_reviews == 10:
            Badge.objects.get_or_create(
                user=instance.user,
                badge_type="reviews_10",
                defaults={
                    "name": "10 sharh",
                    "description": "10 ta sharh yozdingiz",
                    "icon": "📝",
                },
            )
        elif gamification.total_reviews == 50:
            Badge.objects.get_or_create(
                user=instance.user,
                badge_type="reviews_50",
                defaults={
                    "name": "50 sharh",
                    "description": "50 ta sharh yozdingiz",
                    "icon": "✍️",
                },
            )
        elif gamification.total_reviews == 100:
            Badge.objects.get_or_create(
                user=instance.user,
                badge_type="reviews_100",
                defaults={
                    "name": "100 sharh",
                    "description": "100 ta sharh yozdingiz!",
                    "icon": "🏆",
                },
            )


@receiver(post_save, sender=ReviewHelpfulVote)
def update_gamification_on_helpful_vote(sender, instance, created, **kwargs):
    """Update review author's gamification when their review gets helpful votes"""
    if not created or kwargs.get("raw", False) or not instance.review.user:
        return

    review = instance.review
    gamification, _ = UserGamification.objects.get_or_create(user=review.user)

    # Update helpful votes count
    total_helpful = ReviewHelpfulVote.objects.filter(
        review__user=review.user, is_helpful=True
    ).count()
    gamification.helpful_votes_received = total_helpful
    gamification.save()

    # Add XP for helpful vote
    if instance.is_helpful:
        gamification.add_xp(2, "Helpful vote received")

    # Award helpful badges
    if total_helpful == 10:
        Badge.objects.get_or_create(
            user=review.user,
            badge_type="helpful_10",
            defaults={
                "name": "10 foydali ovoz",
                "description": "Sharhlaringiz 10 ta foydali ovoz oldi",
                "icon": "👍",
            },
        )
    elif total_helpful == 50:
        Badge.objects.get_or_create(
            user=review.user,
            badge_type="helpful_50",
            defaults={
                "name": "50 foydali ovoz",
                "description": "Sharhlaringiz 50 ta foydali ovoz oldi",
                "icon": "🌟",
            },
        )
    elif total_helpful == 100:
        Badge.objects.get_or_create(
            user=review.user,
            badge_type="helpful_100",
            defaults={
                "name": "100 foydali ovoz",
                "description": "Sharhlaringiz 100 ta foydali ovoz oldi!",
                "icon": "💎",
            },
        )


@receiver(pre_save, sender=ReviewImage)
def optimize_review_image(sender, instance, **kwargs):
    """Optimize review images before saving"""
    if instance.image:
        try:
            if instance.pk:
                old_instance = ReviewImage.objects.get(pk=instance.pk)
                if old_instance.image != instance.image:
                    from .image_optimization import optimize_image

                    optimized = optimize_image(
                        instance.image, max_width=1200, max_height=900, quality=85
                    )
                    if optimized:
                        instance.image = optimized
            else:
                from .image_optimization import optimize_image

                optimized = optimize_image(
                    instance.image, max_width=1200, max_height=900, quality=85
                )
                if optimized:
                    instance.image = optimized
        except ReviewImage.DoesNotExist:
            pass
