from django.core.management.base import BaseCommand, CommandError
from frontend.sms import send_otp_via_eskiz


class Command(BaseCommand):
    help = "Send a test OTP SMS via Eskiz to the given phone number (digits only, e.g., 998901234567)."

    def add_arguments(self, parser):
        parser.add_argument('phone', type=str, help='Recipient phone in international digits (e.g., 998901234567)')

    def handle(self, *args, **options):
        phone = options['phone']
        import re
        phone_digits = re.sub(r"\D+", "", phone)
        if not (phone_digits.startswith('998') and len(phone_digits) == 12):
            raise CommandError('Phone must be 12 digits starting with 998, e.g., 998901234567')
        code = '123456'
        ok = send_otp_via_eskiz(phone_digits, code)
        if ok:
            self.stdout.write(self.style.SUCCESS(f"Test SMS sent (or printed in DEBUG) to {phone_digits}. Code: {code}"))
        else:
            raise CommandError('Failed to send test SMS via Eskiz')
