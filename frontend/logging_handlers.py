import logging
import traceback


class TelegramErrorHandler(logging.Handler):
    """Send ERROR logs to Telegram admin/review groups using existing bot setup."""

    IGNORED_PATTERNS = (
        "cancellederror",
        "asyncio.exceptions.cancellederror",
        "client disconnected",
        "broken pipe",
        "connection reset by peer",
        "forbidden: bot was blocked by the user",
        "chat not found",
        "bot was blocked by the user",
    )

    def _should_skip(self, record, message: str) -> bool:
        if record.levelno < logging.ERROR:
            return True

        low = (message or "").lower()
        if any(pattern in low for pattern in self.IGNORED_PATTERNS):
            return True

        if record.exc_info and record.exc_info[0] is not None:
            exc_name = getattr(record.exc_info[0], "__name__", "").lower()
            if "cancellederror" in exc_name:
                return True

        return False

    def emit(self, record):
        try:
            from django.conf import settings
            from .utils import send_telegram_message

            message = self.format(record)
            if self._should_skip(record, message):
                return

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
