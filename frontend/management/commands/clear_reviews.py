from django.core.management.base import BaseCommand
from django.db import transaction
from frontend.models import Review, Company


class Command(BaseCommand):
    help = "Delete all reviews and reset company aggregates (rating, review_count) to zero."

    def handle(self, *args, **options):
        with transaction.atomic():
            deleted_count, _ = Review.objects.all().delete()
            updated = Company.objects.update(rating=0, review_count=0)

        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted_count} reviews; reset {updated} companies."
            )
        )
