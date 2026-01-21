from django import template
from django.urls import translate_url

register = template.Library()


@register.simple_tag(takes_context=True)
def get_translated_url(context, lang_code):
    request = context.get("request")
    if not request:
        return ""

    full_path = request.get_full_path()

    # Manual fallback because translate_url can be flaky with some configs
    # Check if current path has /ru/ prefix
    if full_path.startswith("/ru/") or full_path == "/ru":
        clean_path = full_path[3:] if full_path.startswith("/ru/") else "/"
    else:
        clean_path = full_path

    if lang_code == "ru":
        if clean_path == "/":
            return "/ru/"
        return "/ru" + clean_path
    elif lang_code == "uz":
        return clean_path

    return translate_url(full_path, lang_code)
