import logging
import traceback


class TelegramErrorHandler(logging.Handler):
    """Send ERROR logs to Telegram admin/review groups using existing bot setup."""

    def emit(self, record):
        try:
            from django.conf import settings
            from .utils import send_telegram_message

            message = self.format(record)
            tb_text = ""
            if record.exc_info:
                tb_text = "\n".join(traceback.format_exception(*record.exc_info))
                tb_text = tb_text[-2500:]

            text = (
                "<b>🚨 Production Error</b>\n"
                f"<b>Level:</b> {record.levelname}\n"
                f"<b>Logger:</b> {record.name}\n"
                f"<b>Message:</b> {message[:1200]}"
            )

            if tb_text:
                text += f"\n\n<b>Traceback:</b>\n<pre>{tb_text}</pre>"

            chat_ids = (
                getattr(settings, "TELEGRAM_ERROR_CHAT_IDS", [])
                or getattr(settings, "TELEGRAM_ADMIN_CHAT_IDS", [])
                or getattr(settings, "TELEGRAM_REVIEWS_CHAT_IDS", [])
            )
            send_telegram_message(text, chat_ids=chat_ids)
        except Exception:
            return
