"""
Management command to send digest emails to users.
Sends weekly or monthly summary emails with activity updates.
"""
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from frontend.models import User, Review, Company
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Send digest emails to users with recent activity'

    def add_arguments(self, parser):
        parser.add_argument(
            '--period',
            type=str,
            default='weekly',
            choices=['weekly', 'monthly'],
            help='Digest period: weekly or monthly',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be sent without actually sending emails',
        )

    def handle(self, *args, **options):
        period = options['period']
        dry_run = options['dry_run']

        # Calculate date range
        if period == 'weekly':
            since_date = timezone.now() - timedelta(days=7)
            period_label = 'haftalik'
        else:
            since_date = timezone.now() - timedelta(days=30)
            period_label = 'oylik'

        # Get active users (who have created content or logged in recently)
        active_users = User.objects.filter(
            last_login__gte=since_date
        ).distinct()

        sent_count = 0
        error_count = 0

        for user in active_users:
            # Skip if user doesn't want emails (if preference exists)
            if hasattr(user, 'userprofile') and not user.userprofile.email_notifications:
                continue

            # Gather statistics for this user
            stats = self._get_user_stats(user, since_date)

            # Skip if no activity
            if not any(stats.values()):
                continue

            if dry_run:
                self.stdout.write(f'Would send {period_label} digest to {user.email}:')
                self.stdout.write(f'  - New reviews on managed companies: {stats["reviews_on_companies"]}')
                self.stdout.write(f'  - Likes on your reviews: {stats["review_likes"]}')
                self.stdout.write(f'  - New followers: {stats["new_followers"]}')
                sent_count += 1
            else:
                # Send email
                try:
                    subject = f'Fikrly {period_label} xulosa'
                    message = self._format_email(user, stats, period_label)
                    
                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        [user.email],
                        fail_silently=False,
                    )
                    sent_count += 1
                    logger.info(f'Sent {period} digest to {user.email}')
                except Exception as e:
                    error_count += 1
                    logger.error(f'Failed to send digest to {user.email}: {e}')

        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would send {sent_count} {period} digest emails'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Sent {sent_count} {period} digest emails ({error_count} errors)')
            )

    def _get_user_stats(self, user, since_date):
        """Gather activity statistics for user."""
        # Reviews on companies the user manages
        managed_companies = Company.objects.filter(manager=user)
        reviews_on_companies = Review.objects.filter(
            company__in=managed_companies,
            created_at__gte=since_date,
            is_approved=True
        ).count()

        # Likes on user's reviews
        user_reviews = Review.objects.filter(author=user)
        review_likes = sum(r.like_count for r in user_reviews)

        # New followers (if social features exist)
        new_followers = 0

        return {
            'reviews_on_companies': reviews_on_companies,
            'review_likes': review_likes,
            'new_followers': new_followers,
        }

    def _format_email(self, user, stats, period_label):
        """Format email message."""
        message = f"""Assalomu alaykum, {user.get_full_name() or user.username}!

Sizning {period_label} Fikrly faoliyatingiz:

"""
        if stats['reviews_on_companies'] > 0:
            message += f"✓ Biznesingizga {stats['reviews_on_companies']} ta yangi sharh qoldirildi\n"
        
        if stats['review_likes'] > 0:
            message += f"✓ Sharhlaringiz {stats['review_likes']} ta yoqtirish oldi\n"
        
        message += f"""
Fikrly platformasida faol bo'lganingiz uchun rahmat!

--
Fikrly jamoasi
{settings.SITE_DOMAIN}
"""
        return message
