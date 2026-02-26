from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from frontend.models import UserProfile, Review
from frontend.utils import send_telegram_message


class Command(BaseCommand):
    help = "Send Telegram report for verified/unverified users and reviews"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Print report without sending Telegram message",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        user_model = get_user_model()
        total_users = user_model.objects.count()
        verified_users = UserProfile.objects.filter(is_approved=True).count()
        unverified_users = max(total_users - verified_users, 0)

        total_reviews = Review.objects.count()
        verified_reviews = Review.objects.filter(is_approved=True).count()
        unverified_reviews = max(total_reviews - verified_reviews, 0)

        message = (
            "<b>📊 3-kunlik holat hisoboti</b>\n"
            f"👤 Foydalanuvchilar: jami <b>{total_users}</b>\n"
            f"✅ Tasdiqlangan: <b>{verified_users}</b>\n"
            f"⏳ Tasdiqlanmagan: <b>{unverified_users}</b>\n\n"
            f"📝 Sharhlar: jami <b>{total_reviews}</b>\n"
            f"✅ Tasdiqlangan: <b>{verified_reviews}</b>\n"
            f"⏳ Tasdiqlanmagan: <b>{unverified_reviews}</b>"
        )

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN: Telegram message not sent"))
            self.stdout.write(message)
            return

        send_telegram_message(message)
        self.stdout.write(self.style.SUCCESS("Stats report sent to Telegram admin chats"))
