"""
Management command to generate XML sitemap for SEO.
Creates sitemap.xml with all public pages.
"""

from django.core.management.base import BaseCommand
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from frontend.models import Company, Review
from frontend.visibility import public_companies_queryset
import os
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Generate XML sitemap for SEO"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="sitemap.xml",
            help="Output file path (default: sitemap.xml in project root)",
        )

    def handle(self, *args, **options):
        output_path = options["output"]

        # Start XML
        sitemap = ['<?xml version="1.0" encoding="UTF-8"?>']
        sitemap.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

        # Add static pages
        static_pages = [
            ("business_list", 1.0, "daily"),
            ("about", 0.5, "monthly"),
        ]

        domain = getattr(settings, "SITE_DOMAIN", "https://fikrly.uz")

        for url_name, priority, changefreq in static_pages:
            try:
                url = reverse(url_name)
                sitemap.append(
                    self._create_url_entry(
                        f"{domain}{url}", priority=priority, changefreq=changefreq
                    )
                )
            except Exception as e:
                logger.warning(f"Could not reverse URL {url_name}: {e}")

        # Add company pages
        active_companies = public_companies_queryset()
        for company in active_companies:
            url = reverse("company_detail", args=[company.pk])
            lastmod = company.updated_at if hasattr(company, "updated_at") else None
            sitemap.append(
                self._create_url_entry(
                    f"{domain}{url}", lastmod=lastmod, priority=0.8, changefreq="weekly"
                )
            )

        # Close XML
        sitemap.append("</urlset>")

        # Write to file
        full_path = os.path.join(settings.BASE_DIR, output_path)

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write("\n".join(sitemap))

            self.stdout.write(
                self.style.SUCCESS(f"Successfully generated sitemap: {full_path}")
            )
            self.stdout.write(f"  - {len(active_companies)} companies")
            self.stdout.write(f"  - {len(static_pages)} static pages")
            logger.info(f"Generated sitemap with {len(active_companies)} companies")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to write sitemap: {e}"))
            logger.error(f"Failed to generate sitemap: {e}")

    def _create_url_entry(self, loc, lastmod=None, priority=None, changefreq=None):
        """Create a single URL entry for the sitemap."""
        entry = ["  <url>"]
        entry.append(f"    <loc>{loc}</loc>")

        if lastmod:
            entry.append(f'    <lastmod>{lastmod.strftime("%Y-%m-%d")}</lastmod>')

        if priority:
            entry.append(f"    <priority>{priority}</priority>")

        if changefreq:
            entry.append(f"    <changefreq>{changefreq}</changefreq>")

        entry.append("  </url>")
        return "\n".join(entry)
