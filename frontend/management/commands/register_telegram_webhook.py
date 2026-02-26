"""Management command to register the Telegram bot webhook.

Usage:
    python manage.py register_telegram_webhook
    python manage.py register_telegram_webhook --site-url https://fikrly.uz
"""
import urllib.request
import urllib.parse
import json

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Register this server's /api/tg/webhook/ URL with the Telegram Bot API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--site-url",
            default=None,
            help="Override the site URL (e.g. https://fikrly.uz). Falls back to SITE_URL setting.",
        )

    def handle(self, *args, **options):
        token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
        if not token:
            self.stderr.write(self.style.ERROR("TELEGRAM_BOT_TOKEN is not set."))
            return

        site_url = options["site_url"] or getattr(settings, "SITE_URL", "")
        if not site_url:
            self.stderr.write(self.style.ERROR(
                "Provide --site-url or set SITE_URL in settings/env."
            ))
            return

        site_url = site_url.rstrip("/")
        webhook_url = f"{site_url}/api/tg/webhook/"

        # Use bot token as secret to verify incoming requests
        secret = getattr(settings, "TELEGRAM_WEBHOOK_SECRET", token)

        payload = {
            "url": webhook_url,
            "allowed_updates": json.dumps(["callback_query", "message"]),
            "secret_token": secret,
            "drop_pending_updates": "true",
        }

        api_url = f"https://api.telegram.org/bot{token}/setWebhook"
        data = urllib.parse.urlencode(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=data)

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read())
        except Exception as exc:
            self.stderr.write(self.style.ERROR(f"Request failed: {exc}"))
            return

        if result.get("ok"):
            self.stdout.write(self.style.SUCCESS(
                f"✅ Webhook registered: {webhook_url}"
            ))
        else:
            self.stderr.write(self.style.ERROR(
                f"❌ Telegram error: {result.get('description', result)}"
            ))
