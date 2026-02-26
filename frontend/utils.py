from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Assessment:
    score: float
    label: str


def compute_assessment(rating: float, review_count: int) -> Assessment:
    # Wilson score/confidence-inspired scoring
    # Base score from avg rating normalized to 0..1
    base = max(0.0, min(1.0, float(rating) / 5.0))
    # Confidence weight: more reviews -> closer to base
    # k controls smoothing (higher = more smoothing)
    k = 50.0
    weight = review_count / (review_count + k)
    score = (0.5 * (1 - weight)) + (base * weight)

    if score >= 0.85:
        label = "Ajoyib"
    elif score >= 0.7:
        label = "Yaxshi"
    elif score >= 0.55:
        label = "O'rtacha"
    else:
        label = "Past"

    return Assessment(score=round(score * 100, 1), label=label)


# --- Notifications / Utilities ---
def send_telegram_review_notification(review) -> None:
    """Send a Telegram notification for a new review with Approve/Reject inline buttons.
    If the review has a receipt image, sends it via sendPhoto (multipart); otherwise sendMessage.
    """
    import json
    import urllib.request
    import urllib.parse
    import io
    import os
    from django.conf import settings

    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_ids = getattr(settings, "TELEGRAM_REVIEWS_CHAT_IDS", [])
    if not token or not chat_ids:
        return

    site_url = getattr(settings, "SITE_URL", "https://fikrly.uz").rstrip("/")
    stars = "⭐" * int(review.rating)
    text = (
        f"🆕 <b>Yangi sharh</b>\n\n"
        f"🏢 <b>Kompaniya:</b> {review.company.name}\n"
        f"👤 <b>Muallif:</b> {review.user_name}\n"
        f"⭐ <b>Baho:</b> {stars} ({review.rating}/5)\n"
        f"📝 <b>Matn:</b> {review.text[:300]}\n\n"
        f"🔗 <a href='{site_url}/company/{review.company.pk}/'>Kompaniyaga o'tish</a>"
    )

    reply_markup = json.dumps({
        "inline_keyboard": [[
            {"text": "✅ Tasdiqlash", "callback_data": f"approve:{review.pk}"},
            {"text": "❌ O'chirish", "callback_data": f"reject:{review.pk}"},
        ]]
    })

    # Check whether there is a receipt image file on disk
    has_receipt = False
    receipt_path = None
    if review.receipt:
        try:
            receipt_path = review.receipt.path
            has_receipt = os.path.isfile(receipt_path)
        except Exception:
            has_receipt = False

    for chat_id in chat_ids:
        try:
            if has_receipt:
                # --- sendPhoto via multipart/form-data ---
                boundary = "TGBotBoundary"
                def _field(name, value):
                    return (
                        f"--{boundary}\r\n"
                        f"Content-Disposition: form-data; name=\"{name}\"\r\n\r\n"
                        f"{value}\r\n"
                    ).encode("utf-8")

                with open(receipt_path, "rb") as fh:
                    file_bytes = fh.read()
                filename = os.path.basename(receipt_path)
                # Determine MIME type
                ext = filename.rsplit(".", 1)[-1].lower()
                mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png",
                        "gif": "image/gif", "webp": "image/webp"}.get(ext, "application/octet-stream")

                body = io.BytesIO()
                body.write(_field("chat_id", str(chat_id)))
                body.write(_field("caption", text[:1024]))
                body.write(_field("parse_mode", "HTML"))
                body.write(_field("reply_markup", reply_markup))
                # file field
                body.write((
                    f"--{boundary}\r\n"
                    f"Content-Disposition: form-data; name=\"photo\"; filename=\"{filename}\"\r\n"
                    f"Content-Type: {mime}\r\n\r\n"
                ).encode("utf-8"))
                body.write(file_bytes)
                body.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))

                body_bytes = body.getvalue()
                url = f"https://api.telegram.org/bot{token}/sendPhoto"
                req = urllib.request.Request(
                    url,
                    data=body_bytes,
                    headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    resp.read()
            else:
                # --- plain sendMessage ---
                base = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": text,
                    "parse_mode": "HTML",
                    "disable_web_page_preview": "true",
                    "reply_markup": reply_markup,
                }
                req = urllib.request.Request(
                    base, data=urllib.parse.urlencode(data).encode("utf-8")
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    resp.read()
        except Exception:
            # If photo send fails, fall back to text-only message
            try:
                base = f"https://api.telegram.org/bot{token}/sendMessage"
                data = {
                    "chat_id": chat_id,
                    "text": text + "\n\n📎 <i>Chek fayli yuborishda xatolik</i>",
                    "parse_mode": "HTML",
                    "disable_web_page_preview": "true",
                    "reply_markup": reply_markup,
                }
                req = urllib.request.Request(
                    base, data=urllib.parse.urlencode(data).encode("utf-8")
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    resp.read()
            except Exception:
                continue


def answer_telegram_callback(callback_query_id: str, text: str, token: str) -> None:
    """Acknowledge a Telegram callback query (removes the loading spinner)."""
    import urllib.request
    import urllib.parse

    try:
        base = f"https://api.telegram.org/bot{token}/answerCallbackQuery"
        data = {"callback_query_id": callback_query_id, "text": text, "show_alert": "false"}
        req = urllib.request.Request(
            base, data=urllib.parse.urlencode(data).encode("utf-8")
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read()
    except Exception:
        pass


def edit_telegram_message(chat_id: str, message_id: int, new_text: str, token: str) -> None:
    """Edit an existing Telegram message after approve/reject."""
    import urllib.request
    import urllib.parse

    try:
        base = f"https://api.telegram.org/bot{token}/editMessageText"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": new_text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        }
        req = urllib.request.Request(
            base, data=urllib.parse.urlencode(data).encode("utf-8")
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            resp.read()
    except Exception:
        pass


def send_ownership_claim_notification(claim) -> None:
    """Send structured Telegram message for a new BusinessOwnershipClaim with Approve/Reject buttons."""
    import json
    import urllib.request
    import urllib.parse
    from django.conf import settings

    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chat_ids = getattr(settings, "TELEGRAM_ADMIN_CHAT_IDS", [])
    if not token or not chat_ids:
        return

    proof_link = ""
    if claim.proof_file:
        try:
            from django.conf import settings as ds
            base_url = getattr(ds, "SITE_URL", "https://fikrly.uz")
            proof_link = f'\n📎 <a href="{base_url}{claim.proof_file.url}">Hujjatni ko\'rish</a>'
        except Exception:
            pass

    position_display = dict(claim.POSITION_CHOICES).get(claim.position, claim.position)
    created = claim.created_at.strftime("%Y-%m-%d %H:%M") if claim.created_at else "—"

    text = (
        f"📢 <b>YANGI BIZNES EGALLASH SO'ROVI</b>\n\n"
        f"🏢 <b>Biznes:</b> {claim.company.name}\n"
        f"🆔 <b>Biznes ID:</b> {claim.company.id}\n"
        f"👤 <b>Ism:</b> {claim.full_name}\n"
        f"📱 <b>Telefon:</b> {claim.phone}\n"
        f"📧 <b>Email:</b> {claim.email}\n\n"
        f"🧾 <b>Lavozim:</b> {position_display}\n"
        f"💬 <b>Izoh:</b> {claim.comment or '—'}"
        f"{proof_link}\n\n"
        f"🗓 <b>Sana:</b> {created}\n"
        f"🆔 <b>So'rov ID:</b> #{claim.id}"
    )

    keyboard = {
        "inline_keyboard": [[
            {"text": "✅ Tasdiqlash", "callback_data": f"claim_approve:{claim.id}"},
            {"text": "❌ Rad etish", "callback_data": f"claim_reject:{claim.id}"},
        ]]
    }

    base = f"https://api.telegram.org/bot{token}/sendMessage"
    last_msg_id = None
    last_chat_id = None
    for chat_id in chat_ids:
        try:
            data = {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": "HTML",
                "disable_web_page_preview": "true",
                "reply_markup": json.dumps(keyboard),
            }
            req = urllib.request.Request(
                base, data=urllib.parse.urlencode(data).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                result = json.loads(resp.read())
                if result.get("ok"):
                    last_msg_id = str(result["result"]["message_id"])
                    last_chat_id = str(chat_id)
        except Exception:
            continue

    # Store message id so we can edit it on approve/reject
    if last_msg_id:
        from frontend.models import BusinessOwnershipClaim
        BusinessOwnershipClaim.objects.filter(pk=claim.id).update(
            telegram_message_id=last_msg_id,
            telegram_chat_id=last_chat_id or "",
        )


def send_telegram_message(message: str, chat_ids: list[str] | None = None) -> None:
    import json
    import urllib.request
    import urllib.parse
    from django.conf import settings

    token = getattr(settings, "TELEGRAM_BOT_TOKEN", "")
    chats = (
        chat_ids
        if chat_ids is not None
        else getattr(settings, "TELEGRAM_ADMIN_CHAT_IDS", [])
    )
    if not token or not chats:
        return

    base = f"https://api.telegram.org/bot{token}/sendMessage"
    payload_base = {
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": "true",
    }
    for chat_id in chats:
        try:
            data = payload_base | {"chat_id": chat_id}
            req = urllib.request.Request(
                base, data=urllib.parse.urlencode(data).encode("utf-8")
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                resp.read()
        except Exception:
            # Ignore failures silently in development
            continue


def diff_instance_fields(instance, changed_data: dict) -> str:
    """Produce a simple details string for changed fields."""
    parts = []
    for k, v in changed_data.items():
        parts.append(f"{k} -> {v}")
    return "; ".join(parts)


def recalculate_company_stats(company_id: int) -> None:
    """Recalculate rating and review_count for a company based on approved reviews."""
    from django.db.models import Avg, Count
    from .models import Company

    try:
        company = Company.objects.get(pk=company_id)
        agg = company.reviews.filter(is_approved=True).aggregate(
            avg=Avg("rating"), cnt=Count("id")
        )
        new_review_count = int(agg.get("cnt") or 0)
        new_rating = round(float(agg.get("avg") or 0.0), 2) if new_review_count else 0

        if company.review_count != new_review_count or float(company.rating) != float(
            new_rating
        ):
            company.review_count = new_review_count
            company.rating = new_rating
            company.save(update_fields=["review_count", "rating"])
    except Company.DoesNotExist:
        pass
