"""
Migrate company logos from external URLs to Cloudflare R2.

Usage:
    python manage.py migrate_logos_to_r2 [--dry-run] [--company-id ID]

Environment variables required:
    R2_BUCKET_NAME
    R2_ENDPOINT
    R2_ACCESS_KEY_ID
    R2_SECRET_ACCESS_KEY
    R2_PUBLIC_URL (optional, defaults to R2_ENDPOINT format)
"""

import os
import io
import requests
from urllib.parse import urlparse
from PIL import Image
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from frontend.models import Company


class Command(BaseCommand):
    help = "Download company logos from URLs and upload to Cloudflare R2"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )
        parser.add_argument(
            '--company-id',
            type=int,
            help='Migrate only specific company by ID',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip companies that already have logo in R2',
        )
        parser.add_argument(
            '--sizes',
            nargs='+',
            type=int,
            default=[64, 256, 512],
            help='Logo sizes to generate (default: 64 256 512)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        company_id = options['company_id']
        skip_existing = options['skip_existing']
        sizes = options['sizes']

        # Check R2 credentials
        self.bucket_name = os.environ.get('R2_BUCKET_NAME')
        self.endpoint = os.environ.get('R2_ENDPOINT')
        self.access_key = os.environ.get('R2_ACCESS_KEY_ID')
        self.secret_key = os.environ.get('R2_SECRET_ACCESS_KEY')
        self.public_url = os.environ.get('R2_PUBLIC_URL', f"https://{self.endpoint.split('/')[2]}")

        if not all([self.bucket_name, self.endpoint, self.access_key, self.secret_key]):
            raise CommandError(
                "Missing R2 credentials. Set these environment variables:\n"
                "  R2_BUCKET_NAME, R2_ENDPOINT, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY"
            )

        # Initialize S3 client
        self.s3 = self._get_s3_client()

        # Get companies to process
        queryset = Company.objects.all()
        if company_id:
            queryset = queryset.filter(id=company_id)
        if skip_existing:
            queryset = queryset.exclude(logo_url__contains=self.public_url)

        # Filter companies with external logo URLs
        companies = [
            c for c in queryset
            if c.logo_url and not c.logo_url.startswith(self.public_url)
        ]

        self.stdout.write(f"Found {len(companies)} companies with external logo URLs")
        self.stdout.write(f"Target bucket: {self.bucket_name}")
        self.stdout.write(f"Public URL base: {self.public_url}")
        self.stdout.write(f"Sizes to generate: {sizes}")
        self.stdout.write("-" * 50)

        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN - No changes will be made"))
            for company in companies:
                self.stdout.write(f"Would process: {company.name} ({company.logo_url[:60]}...)")
            return

        # Process each company
        success_count = 0
        error_count = 0
        skipped_count = 0

        for company in companies:
            result = self.process_company(company, sizes)
            if result == 'success':
                success_count += 1
            elif result == 'skipped':
                skipped_count += 1
            else:
                error_count += 1

        self.stdout.write("-" * 50)
        self.stdout.write(self.style.SUCCESS(f"Success: {success_count}"))
        self.stdout.write(self.style.WARNING(f"Skipped: {skipped_count}"))
        self.stdout.write(self.style.ERROR(f"Errors: {error_count}"))

    def _get_s3_client(self):
        """Initialize boto3 S3 client for R2."""
        try:
            import boto3
            from botocore.config import Config

            return boto3.client(
                's3',
                endpoint_url=self.endpoint,
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                config=Config(signature_version='s3v4'),
                region_name='auto'
            )
        except ImportError:
            raise CommandError(
                "boto3 not installed. Run: pip install boto3 Pillow requests"
            )

    def process_company(self, company: Company, sizes: list) -> str:
        """Process a single company logo."""
        logo_url = company.logo_url
        if not logo_url:
            return 'skipped'

        self.stdout.write(f"\nProcessing: {company.name}")
        self.stdout.write(f"  Source: {logo_url[:70]}...")

        try:
            # Download image
            response = requests.get(logo_url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (compatible; LogoBot/1.0)'
            })
            response.raise_for_status()
            img_data = response.content

            # Validate it's an image
            img = Image.open(io.BytesIO(img_data))
            original_format = img.format or 'PNG'
            self.stdout.write(f"  Original: {img.size[0]}x{img.size[1]} {original_format}")

            # Generate and upload each size
            r2_urls = {}
            for size in sizes:
                resized_img = self._resize_image(img, size)
                filename = f"company_logos/{company.id}_{size}.webp"
                
                # Convert to WebP
                buffer = io.BytesIO()
                resized_img.save(buffer, format='WEBP', quality=85, method=6)
                buffer.seek(0)

                # Upload to R2
                self.s3.upload_fileobj(
                    buffer,
                    self.bucket_name,
                    filename,
                    ExtraArgs={
                        'ContentType': 'image/webp',
                        'CacheControl': 'public, max-age=31536000',
                    }
                )
                
                r2_urls[size] = f"{self.public_url}/{filename}"
                self.stdout.write(f"  Uploaded {size}px: {r2_urls[size][:60]}...")

            # Update company - use 256px as default logo_url
            company.logo_url = r2_urls.get(256, r2_urls.get(sizes[0]))
            company.save(update_fields=['logo_url'])

            self.stdout.write(self.style.SUCCESS(f"  Updated company {company.id}"))
            return 'success'

        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f"  Download failed: {e}"))
            return 'error'
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"  Error: {e}"))
            return 'error'

    def _resize_image(self, img: Image.Image, target_size: int) -> Image.Image:
        """Resize image to target size maintaining aspect ratio."""
        img_copy = img.copy()
        img_copy.thumbnail((target_size, target_size), Image.Resampling.LANCZOS)
        
        # Convert to RGBA if necessary for WebP
        if img_copy.mode in ('P', 'LA', 'L'):
            img_copy = img_copy.convert('RGBA')
        elif img_copy.mode != 'RGBA' and img_copy.mode != 'RGB':
            img_copy = img_copy.convert('RGB')
            
        return img_copy
