from django import template
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import datetime

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
