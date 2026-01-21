import os
from django import template
from django.templatetags.static import static
from django.conf import settings

register = template.Library()


@register.simple_tag
def static_bust(path: str) -> str:
    """
    Return static URL with a cache-busting query param based on file mtime.
    """
    url = static(path)

    # Try to resolve absolute path from STATICFILES_DIRS
    mtime = None
    for base in getattr(settings, "STATICFILES_DIRS", []):
        abs_path = os.path.join(str(base), path)
        if os.path.exists(abs_path):
            try:
                mtime = int(os.path.getmtime(abs_path))
                break
            except OSError:
                continue

    # Fallback to STATIC_ROOT during collectstatic runs
    if mtime is None and getattr(settings, "STATIC_ROOT", None):
        abs_path = os.path.join(str(settings.STATIC_ROOT), path)
        if os.path.exists(abs_path):
            try:
                mtime = int(os.path.getmtime(abs_path))
            except OSError:
                mtime = None

    if mtime is None:
        return url

    sep = "&" if "?" in url else "?"
    return f"{url}{sep}v={mtime}"
