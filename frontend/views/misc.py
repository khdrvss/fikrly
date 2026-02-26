"""Miscellaneous views: language switch, static pages, system utilities."""

import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.http import FileResponse, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.cache import cache_control

from ..forms import ContactForm
from ..models import Company
from ..utils import send_telegram_message

logger = logging.getLogger(__name__)


def safe_set_language(request):
    """Compatibility language switcher for both legacy form posts and link-based UI."""
    language = (
        request.POST.get("language")
        or request.GET.get("language")
        or request.POST.get("lang")
        or request.GET.get("lang")
        or "uz"
    )
    next_url = (
        request.POST.get("next")
        or request.GET.get("next")
        or request.META.get("HTTP_REFERER")
        or "/"
    )

    allowed_hosts = {request.get_host()} if request.get_host() else None
    if not url_has_allowed_host_and_scheme(
        url=next_url,
        allowed_hosts=allowed_hosts,
        require_https=request.is_secure(),
    ):
        next_url = "/"

    if not next_url.startswith("/"):
        next_url = "/"

    if language == "uz":
        if next_url == "/ru":
            next_url = "/"
        elif next_url.startswith("/ru/"):
            next_url = next_url[3:]
    elif language == "ru":
        if next_url == "/":
            next_url = "/ru/"
        elif next_url == "/ru":
            next_url = "/ru/"
        elif not next_url.startswith("/ru/"):
            next_url = f"/ru{next_url}"
    else:
        language = "uz"

    response = redirect(next_url)
    response.set_cookie(
        settings.LANGUAGE_COOKIE_NAME,
        language,
        max_age=365 * 24 * 60 * 60,
        path=settings.LANGUAGE_COOKIE_PATH,
        domain=settings.LANGUAGE_COOKIE_DOMAIN,
        secure=settings.LANGUAGE_COOKIE_SECURE,
        httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
        samesite=settings.LANGUAGE_COOKIE_SAMESITE,
    )
    return response


def privacy_policy(request):
    """Static privacy policy page."""
    return render(request, "pages/privacy_policy.html")


def terms_of_service(request):
    """Static Terms of Service page."""
    return render(request, "pages/terms_of_service.html")


def community_guidelines(request):
    """Static Community Guidelines page."""
    return render(request, "pages/community_guidelines.html")


def contact_us(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            subject = form.cleaned_data["subject"]
            message = form.cleaned_data["message"]

            full_message = f"Yuboruvchi: {name} <{email}>\n\n{message}"
            try:
                email_msg = EmailMessage(
                    subject=f"[Fikrly Contact] {subject}",
                    body=full_message,
                    from_email=None,
                    to=["fikrlyuzb@gmail.com"],
                    reply_to=[email],
                )
                email_msg.send(fail_silently=False)
                send_telegram_message(
                    f"📩 <b>Yangi xabar</b>\nKimdan: {name}\nEmail: {email}\nMavzu: {subject}\n\n{message[:200]}..."
                )
            except Exception as e:
                logger.warning("Email sending failed: %s", e)

            messages.success(
                request, "Xabaringiz yuborildi. Tez orada siz bilan bog'lanamiz."
            )
            return redirect("contact_us")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial["name"] = (
                f"{request.user.first_name} {request.user.last_name}".strip()
                or request.user.username
            )
            initial["email"] = request.user.email
        form = ContactForm(initial=initial)

    return render(request, "pages/contact_us.html", {"form": form})


@cache_control(max_age=86400)
def robots_txt(request):
    scheme = request.scheme
    host = request.get_host()
    sitemap_url = f"{scheme}://{host}/sitemap.xml"
    content = (
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Disallow: /accounts/\n"
        "\n"
        f"Sitemap: {sitemap_url}\n"
    )
    return HttpResponse(content, content_type="text/plain")


def bing_site_auth(request):
    content = (
        '<?xml version="1.0"?>\n'
        "<users>\n"
        "	<user>87C31115864528DD0984DF2E125A313E</user>\n"
        "</users>"
    )
    return HttpResponse(content, content_type="application/xml")


def favicon_file(request):
    for path in [
        settings.STATIC_ROOT / "favicons" / "favicon.ico",
        settings.STATIC_ROOT / "favicon.ico",
        settings.BASE_DIR / "frontend" / "static" / "favicons" / "favicon.ico",
        settings.BASE_DIR / "public" / "favicon.ico",
    ]:
        if path.exists():
            return FileResponse(open(path, "rb"), content_type="image/x-icon")
    return HttpResponse(status=404)


def service_worker(request):
    """Serve the service worker JS for PWA."""
    for path in [
        settings.STATIC_ROOT / "service-worker.js",
        settings.BASE_DIR / "frontend" / "static" / "service-worker.js",
    ]:
        if path.exists():
            response = FileResponse(open(path, "rb"), content_type="application/javascript")
            response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response
    return HttpResponse(status=404)


def health_check(request):
    """Health check endpoint for monitoring."""
    import time
    from django.db import connection

    health_status = {"status": "healthy", "timestamp": time.time(), "checks": {}}

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["checks"]["database"] = f"error: {str(e)}"
        health_status["status"] = "unhealthy"
        logger.error("Database health check failed: %s", e)

    try:
        cache.set("health_check", "ok", 10)
        if cache.get("health_check") == "ok":
            health_status["checks"]["cache"] = "ok"
        else:
            health_status["checks"]["cache"] = "error: cache not working"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["cache"] = f"error: {str(e)}"
        health_status["status"] = "degraded"
        logger.error("Cache health check failed: %s", e)

    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_percent = (free / total) * 100
        if free_percent > 10:
            health_status["checks"]["disk"] = f"ok ({free_percent:.1f}% free)"
        else:
            health_status["checks"]["disk"] = f"warning ({free_percent:.1f}% free)"
            health_status["status"] = "degraded"
    except Exception as e:
        health_status["checks"]["disk"] = f"error: {str(e)}"
        logger.error("Disk health check failed: %s", e)

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JsonResponse(health_status, status=status_code)


def ratelimit_error(request, exception=None):
    """Custom view for rate limit errors."""
    return JsonResponse(
        {
            "error": "Too many requests",
            "detail": "Juda ko'p so'rov yuborildi. Iltimos, bir necha daqiqadan so'ng qayta urinib ko'ring.",
            "retry_after": 60,
        },
        status=429,
    )


def widgets_page(request):
    """Public /widgets/ marketing page — teaches businesses how to install the badge widget."""
    # Pick the first active company for live iframed demos, fall back to None.
    demo_company = Company.objects.filter(is_active=True).order_by("-review_count").first()
    demo_pk = demo_company.pk if demo_company else None

    # If the visitor is a logged-in business manager, surface their company ID
    # so the "Kod olish" modal can generate personalised embed code.
    user_company = None
    if request.user.is_authenticated:
        user_company = Company.objects.filter(manager=request.user, is_active=True).first()

    faq = [
        {
            "q": "iframe o'rnatish xavfsizmi?",
            "a": "Ha, iframe — eng keng tarqalgan va xavfsiz embed usuli. U sizning saytingizning hech qanday ma'lumotiga kirish imkoniga ega emas. Stripe, Trustpilot va boshqa yirik platformalar ham aynan shu usuldan foydalanadi.",
        },
        {
            "q": "Bu saytimning SEO'siga ta'sir qiladimi?",
            "a": "Ijobiy ta'sir ko'rsatadi. Har bir widget fikrly.uz ga sifatli backlink beradi. Bundan tashqari, reyting ko'rsatish sahifangizda foydalanuvchilarni ko'proq vaqt ushlab turadi (dwell time), bu ham SEO signali hisoblanadi.",
        },
        {
            "q": "Reytinglar real vaqt yangilanadimi?",
            "a": "Ha. Widget sahifasi 5 daqiqa kesh qilinadi, shuning uchun yangi sharh qo'shilgandan so'ng 5 daqiqa ichida widget yangilanadi.",
        },
        {
            "q": "Qanday qilib kompaniya IDni topaman?",
            "a": "Biznes dashboardingizga kiring — 'Saytingizga badge qo'shing' bo'limida tayyor kod mavjud. Yoki saytdagi kompaniya sahifasining URL'idan ham ko'rishingiz mumkin: fikrly.uz/bizneslar/123/ — bu yerda 123 sizning ID ingiz.",
        },
        {
            "q": "Widget mobil qurilmalarda ishlaydi, to'g'rimi?",
            "a": "Ha. sm o'lchamini tanlasangiz mobilga mukammal mos keladi. Shuningdek, size=sm parametrini iframe'ning CSS display:block va max-width:100% bilan birga ishlatsangiz, barcha ekran o'lchamlarida to'g'ri ko'rinadi.",
        },
        {
            "q": "Dark mode bilan ishlaydi?",
            "a": "Ha. ?theme=dark parametrini qo'shing yoki ?theme=auto — bu holda foydalanuvchining OS rangiga avtomatik moslashadi.",
        },
    ]

    return render(request, "pages/widgets.html", {
        "demo_pk": demo_pk,
        "user_company": user_company,
        "faq": faq,
    })
