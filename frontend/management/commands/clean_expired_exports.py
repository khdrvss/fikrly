"""
Management command to clean up expired data exports.
Deletes export files older than 7 days.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from frontend.models import DataExport
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Clean up expired data export files (older than 7 days)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Number of days to keep exports (default: 7)',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        days = options['days']
        dry_run = options['dry_run']
        cutoff_date = timezone.now() - timedelta(days=days)

        # Find expired exports
        expired_exports = DataExport.objects.filter(
            completed_at__lt=cutoff_date,
            status='completed'
        )

        count = expired_exports.count()

        if count == 0:
            self.stdout.write(self.style.SUCCESS(f'No expired exports found (older than {days} days)'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING(f'DRY RUN: Would delete {count} exports:'))
            for export in expired_exports:
                self.stdout.write(f'  - Export #{export.id} ({export.format}) from {export.completed_at}')
        else:
            # Delete files and records
            deleted_files = 0
            for export in expired_exports:
                if export.file:
                    try:
                        export.file.delete(save=False)
                        deleted_files += 1
                    except Exception as e:
                        logger.error(f'Failed to delete file for export #{export.id}: {e}')

            # Delete records
            deleted_count, _ = expired_exports.delete()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted_count} exports and {deleted_files} files (older than {days} days)'
                )
            )
            logger.info(f'Cleaned up {deleted_count} expired exports')
