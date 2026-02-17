"""Email notification system for user engagement."""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth import get_user_model
from celery import shared_task
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class EmailNotificationService:
    """Service for sending email notifications."""

    FROM_EMAIL = settings.DEFAULT_FROM_EMAIL

    @staticmethod
    def send_html_email(subject, template_name, context, to_email):
        """Send HTML email with fallback to plain text."""
        try:
            html_content = render_to_string(template_name, context)
            text_content = strip_tags(html_content)

            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=EmailNotificationService.FROM_EMAIL,
                to=[to_email],
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

            logger.info(f"Email sent to {to_email}: {subject}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    @classmethod
    def send_review_response_notification(cls, review, owner_response):
        """Notify user when company owner responds to their review."""
        if not review.user or not review.user.email:
            return False

        context = {
            "user_name": review.user.get_full_name() or review.user.username,
            "company_name": review.company.name,
            "review_text": (
                review.text[:100] + "..." if len(review.text) > 100 else review.text
            ),
            "response_text": owner_response,
            "review_url": f"{settings.SITE_URL}/company/{review.company.id}/#review-{review.id}",
            "company_url": f"{settings.SITE_URL}/company/{review.company.id}/",
        }

        return cls.send_html_email(
            subject=f"Javob keldi: {review.company.name}",
            template_name="frontend/emails/review_response.html",
            context=context,
            to_email=review.user.email,
        )

    @classmethod
    def send_review_approved_notification(cls, review):
        """Notify user when their review is approved."""
        if not review.user or not review.user.email:
            return False

        context = {
            "user_name": review.user.get_full_name() or review.user.username,
            "company_name": review.company.name,
            "review_url": f"{settings.SITE_URL}/company/{review.company.id}/#review-{review.id}",
        }

        return cls.send_html_email(
            subject=f"Sizning sharh tasdiqlandi: {review.company.name}",
            template_name="frontend/emails/review_approved.html",
            context=context,
            to_email=review.user.email,
        )

    @classmethod
    def send_helpful_vote_notification(cls, review, voter_count):
        """Notify user when their review receives helpful votes."""
        if not review.user or not review.user.email:
            return False

        # Only send after milestones: 5, 10, 25, 50, 100
        milestones = [5, 10, 25, 50, 100]
        if voter_count not in milestones:
            return False

        context = {
            "user_name": review.user.get_full_name() or review.user.username,
            "company_name": review.company.name,
            "vote_count": voter_count,
            "review_url": f"{settings.SITE_URL}/company/{review.company.id}/#review-{review.id}",
        }

        return cls.send_html_email(
            subject=f"Sharhingiz {voter_count} ta foydali ovoz oldi!",
            template_name="frontend/emails/helpful_milestone.html",
            context=context,
            to_email=review.user.email,
        )

    @classmethod
    def send_new_review_notification(cls, company, review):
        """Notify company manager about new review."""
        if not company.manager or not company.manager.email:
            return False

        context = {
            "manager_name": company.manager.get_full_name() or company.manager.username,
            "company_name": company.name,
            "reviewer_name": review.user.get_full_name() if review.user else "Anonim",
            "rating": review.rating,
            "review_text": (
                review.text[:200] + "..." if len(review.text) > 200 else review.text
            ),
            "review_url": f"{settings.SITE_URL}/company/{company.id}/#review-{review.id}",
            "respond_url": f"{settings.SITE_URL}/company/{company.id}/manage/",
        }

        return cls.send_html_email(
            subject=f"Yangi sharh: {company.name}",
            template_name="frontend/emails/new_review_to_owner.html",
            context=context,
            to_email=company.manager.email,
        )

    @classmethod
    def send_weekly_digest(cls, user, stats):
        """Send weekly activity digest to user."""
        if not user.email:
            return False

        context = {
            "user_name": user.get_full_name() or user.username,
            "reviews_count": stats.get("reviews_count", 0),
            "helpful_votes": stats.get("helpful_votes", 0),
            "new_responses": stats.get("new_responses", 0),
            "trending_companies": stats.get("trending_companies", []),
            "profile_url": f"{settings.SITE_URL}/profile/",
        }

        return cls.send_html_email(
            subject="Sizning haftalik Fikrly xulosangiz",
            template_name="frontend/emails/weekly_digest.html",
            context=context,
            to_email=user.email,
        )


# Celery tasks for async email sending
@shared_task
def send_review_response_email(review_id, owner_response):
    """Async task to send review response notification."""
    from frontend.models import Review

    try:
        review = Review.objects.select_related("user", "company").get(id=review_id)
        EmailNotificationService.send_review_response_notification(
            review, owner_response
        )
    except Review.DoesNotExist:
        logger.error(f"Review {review_id} not found for email notification")


@shared_task
def send_review_approved_email(review_id):
    """Async task to send review approved notification."""
    from frontend.models import Review

    try:
        review = Review.objects.select_related("user", "company").get(id=review_id)
        EmailNotificationService.send_review_approved_notification(review)
    except Review.DoesNotExist:
        logger.error(f"Review {review_id} not found for email notification")


@shared_task
def send_helpful_vote_email(review_id, voter_count):
    """Async task to send helpful vote milestone notification."""
    from frontend.models import Review

    try:
        review = Review.objects.select_related("user", "company").get(id=review_id)
        EmailNotificationService.send_helpful_vote_notification(review, voter_count)
    except Review.DoesNotExist:
        logger.error(f"Review {review_id} not found for email notification")


@shared_task
def send_new_review_email(company_id, review_id):
    """Async task to send new review notification to company owner."""
    from frontend.models import Company, Review

    try:
        company = Company.objects.select_related("manager").get(id=company_id)
        review = Review.objects.select_related("user").get(id=review_id)
        EmailNotificationService.send_new_review_notification(company, review)
    except (Company.DoesNotExist, Review.DoesNotExist) as e:
        logger.error(f"Failed to send new review email: {e}")


@shared_task
def send_weekly_digests():
    """Celery beat task to send weekly digests to all active users."""
    from frontend.models import Review, Company
    from django.utils import timezone
    from datetime import timedelta

    one_week_ago = timezone.now() - timedelta(days=7)

    # Get users with activity in last week
    active_users = User.objects.filter(review__created_at__gte=one_week_ago).distinct()

    # Get trending companies for the digest (top 3 rated)
    trending = list(
        Company.objects.filter(is_active=True, rating__gt=4.0).order_by(
            "-rating", "-review_count"
        )[:3]
    )

    for user in active_users:
        # Compile stats
        user_reviews = Review.objects.filter(user=user, created_at__gte=one_week_ago)
        stats = {
            "reviews_count": user_reviews.count(),
            "helpful_votes": sum(r.helpful_count for r in user_reviews),
            "new_responses": user_reviews.exclude(owner_response_text="").count(),
            "trending_companies": trending,
        }

        EmailNotificationService.send_weekly_digest(user, stats)
