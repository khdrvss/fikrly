from django import template
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime
import hashlib

register = template.Library()

DAYS_MAP = {
    "monday": _("Dushanba"),
    "tuesday": _("Seshanba"),
    "wednesday": _("Chorshanba"),
    "thursday": _("Payshanba"),
    "friday": _("Juma"),
    "saturday": _("Shanba"),
    "sunday": _("Yakshanba"),
}

ORDERED_DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]


@register.filter
def format_working_hours(working_hours):
    """
    Formats working hours JSON into a list of displayable strings.
    Expected format: {"monday": "09:00-18:00", ...}
    """
    if not working_hours or not isinstance(working_hours, dict):
        return []

    formatted = []
    for day in ORDERED_DAYS:
        if day in working_hours:
            time_range = working_hours[day]
            day_name = DAYS_MAP.get(day, day.title())
            formatted.append(
                {
                    "day": day_name,
                    "hours": time_range,
                    "is_today": day == timezone.now().strftime("%A").lower(),
                }
            )
    return formatted


@register.simple_tag
def is_open_now(working_hours):
    """
    Determines if the company is currently open.
    Returns a dict with 'status' (bool) and 'text' (str).
    """
    if not working_hours or not isinstance(working_hours, dict):
        return {"status": False, "text": _("Ma'lumot yo'q")}

    now = timezone.localtime(timezone.now())
    current_day = now.strftime("%A").lower()
    current_time = now.time()

    if current_day not in working_hours:
        return {"status": False, "text": _("Yopiq")}

    hours_str = working_hours[current_day]
    if not hours_str or hours_str.lower() == "closed":
        return {"status": False, "text": _("Yopiq")}

    try:
        start_str, end_str = hours_str.split("-")
        start_time = datetime.datetime.strptime(start_str.strip(), "%H:%M").time()
        end_time = datetime.datetime.strptime(end_str.strip(), "%H:%M").time()

        if start_time <= current_time <= end_time:
            return {"status": True, "text": _("Ochiq")}
        else:
            return {"status": False, "text": _("Yopiq")}
    except ValueError:
        return {"status": False, "text": _("Noma'lum")}


AVATAR_GRADIENTS = [
    "from-emerald-400 to-emerald-500",
    "from-sky-400 to-blue-500",
    "from-violet-400 to-purple-500",
    "from-pink-400 to-rose-500",
    "from-amber-400 to-orange-500",
    "from-cyan-400 to-teal-500",
    "from-lime-400 to-green-500",
    "from-fuchsia-400 to-indigo-500",
]


@register.filter
def avatar_gradient(value):
    seed = str(value or "anonymous")
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    index = int(digest[:8], 16) % len(AVATAR_GRADIENTS)
    return AVATAR_GRADIENTS[index]


@register.filter
def avatar_style(value):
    seed = str(value or "anonymous")
    digest = hashlib.md5(seed.encode("utf-8")).hexdigest()
    gradients = [
        ("#ef4444", "#dc2626"),  # red
        ("#f59e0b", "#d97706"),  # amber
        ("#84cc16", "#65a30d"),  # lime
        ("#10b981", "#059669"),  # emerald
        ("#06b6d4", "#0891b2"),  # cyan
        ("#3b82f6", "#2563eb"),  # blue
        ("#6366f1", "#4f46e5"),  # indigo
        ("#8b5cf6", "#7c3aed"),  # violet
        ("#d946ef", "#c026d3"),  # fuchsia
        ("#ec4899", "#db2777"),  # pink
        ("#14b8a6", "#0d9488"),  # teal
        ("#f97316", "#ea580c"),  # orange
    ]
    index = int(digest[:8], 16) % len(gradients)
    c1, c2 = gradients[index]
    return (
        f"background-color: {c1}; "
        f"background-image: linear-gradient(135deg, {c1}, {c2});"
    )
