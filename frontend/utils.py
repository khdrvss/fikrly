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
def send_telegram_message(message: str, chat_ids: list[str] | None = None) -> None:
    """Send a Telegram message to all admin chat IDs if configured.
    Best-effort: swallow exceptions in dev to avoid breaking flows.
    """
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
