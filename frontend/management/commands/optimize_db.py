"""Management command to optimize database performance."""

from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "Analyze and optimize database performance"

    def add_arguments(self, parser):
        parser.add_argument(
            "--vacuum",
            action="store_true",
            help="Run VACUUM on PostgreSQL database",
        )
        parser.add_argument(
            "--analyze",
            action="store_true",
            help="Run ANALYZE on PostgreSQL database",
        )
        parser.add_argument(
            "--stats",
            action="store_true",
            help="Show database statistics",
        )

    def handle(self, *args, **options):
        if options["vacuum"]:
            self.vacuum_database()

        if options["analyze"]:
            self.analyze_database()

        if options["stats"]:
            self.show_statistics()

        if not any([options["vacuum"], options["analyze"], options["stats"]]):
            self.stdout.write(
                self.style.WARNING("No action specified. Use --help for options.")
            )

    def vacuum_database(self):
        """Run VACUUM on PostgreSQL to reclaim storage."""
        with connection.cursor() as cursor:
            try:
                self.stdout.write("Running VACUUM...")
                cursor.execute("VACUUM ANALYZE;")
                self.stdout.write(self.style.SUCCESS("✓ VACUUM completed successfully"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ VACUUM failed: {e}"))

    def analyze_database(self):
        """Run ANALYZE to update query planner statistics."""
        with connection.cursor() as cursor:
            try:
                self.stdout.write("Running ANALYZE...")
                cursor.execute("ANALYZE;")
                self.stdout.write(
                    self.style.SUCCESS("✓ ANALYZE completed successfully")
                )
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"✗ ANALYZE failed: {e}"))

    def show_statistics(self):
        """Show database statistics."""
        from frontend.models import Company, Review, UserProfile, BusinessCategory

        self.stdout.write(self.style.SUCCESS("\n📊 Database Statistics:\n"))

        stats = [
            ("Companies", Company.objects.count()),
            ("Active Companies", Company.objects.filter(is_active=True).count()),
            ("Reviews", Review.objects.count()),
            ("Approved Reviews", Review.objects.filter(is_approved=True).count()),
            ("Users", UserProfile.objects.count()),
            ("Categories", BusinessCategory.objects.count()),
        ]

        max_label_len = max(len(label) for label, _ in stats)

        for label, count in stats:
            self.stdout.write(f"  {label.ljust(max_label_len)}: {count:,}")

        # Show cache statistics if available
        self.stdout.write(self.style.SUCCESS("\n💾 Cache Statistics:\n"))
        from django.core.cache import cache

        try:
            cache_stats = cache._cache.get_stats()
            if cache_stats:
                for key, value in cache_stats[0].items():
                    self.stdout.write(f"  {key}: {value}")
            else:
                self.stdout.write("  Cache statistics not available")
        except Exception:
            self.stdout.write("  Cache statistics not available")

        # Show index usage (PostgreSQL only)
        if connection.vendor == "postgresql":
            self.stdout.write(self.style.SUCCESS("\n🔍 Index Usage:\n"))
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT 
                        schemaname,
                        tablename,
                        indexname,
                        idx_scan as scans,
                        idx_tup_read as tuples_read,
                        idx_tup_fetch as tuples_fetched
                    FROM pg_stat_user_indexes
                    WHERE schemaname = 'public'
                    ORDER BY idx_scan DESC
                    LIMIT 10;
                """
                )

                rows = cursor.fetchall()
                if rows:
                    self.stdout.write(f'  {"Index".ljust(40)} Scans    Tuples')
                    self.stdout.write("  " + "-" * 60)
                    for row in rows:
                        self.stdout.write(f"  {row[2].ljust(40)} {row[3]:<8} {row[4]}")
                else:
                    self.stdout.write("  No index statistics available")
