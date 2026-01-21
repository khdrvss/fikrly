from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = "Send a test email using current Django email settings"

    def add_arguments(self, parser):
        parser.add_argument("--to", required=True, help="Recipient email address")
        parser.add_argument("--subject", default="Fikrly test email")
        parser.add_argument("--message", default="This is a test email from Fikrly.")

    def handle(self, *args, **options):
        to_email = options["to"]
        subject = options["subject"]
        message = options["message"]
        try:
            sent = send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
            if sent:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Sent to {to_email} via {settings.EMAIL_BACKEND}"
                    )
                )
            else:
                self.stdout.write(self.style.WARNING("send_mail returned 0"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Failed: {e}"))
