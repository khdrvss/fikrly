from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.db import connection
import time


class UzbekDefaultLocaleMiddleware:
    """
    Custom locale middleware that activates Russian only when the URL has the
    /ru/ prefix or the user has explicitly chosen Russian via the language
    switcher.  It deliberately ignores the browser's Accept-Language header so
    Uzbek is always the default for new visitors regardless of browser settings.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from django.utils import translation

        path = request.path_info

        # Language is determined solely by the URL prefix.
        # /ru/... → Russian; everything else → Uzbek (the site default).
        # Browser Accept-Language headers are intentionally ignored so new
        # visitors always land on Uzbek regardless of browser settings.
        lang = "ru" if (path.startswith("/ru/") or path == "/ru") else "uz"

        translation.activate(lang)
        request.LANGUAGE_CODE = lang

        response = self.get_response(request)

        # Keep the language cookie in sync so Django's set_language view and
        # other per-request helpers see the correct value.
        response.set_cookie(
            settings.LANGUAGE_COOKIE_NAME,
            lang,
            max_age=365 * 24 * 60 * 60,  # 1 year
            path=settings.LANGUAGE_COOKIE_PATH,
            domain=settings.LANGUAGE_COOKIE_DOMAIN,
            secure=settings.LANGUAGE_COOKIE_SECURE,
            httponly=settings.LANGUAGE_COOKIE_HTTPONLY,
            samesite=settings.LANGUAGE_COOKIE_SAMESITE,
        )

        translation.deactivate()
        return response


class NoCacheMiddleware(MiddlewareMixin):
    """Disable client-side caching for HTML/JSON responses."""

    def process_response(self, request, response):
        if request.path.startswith("/accounts/"):
            response["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
            return response

        content_type = response.get("Content-Type", "")
        if content_type.startswith("text/html") or content_type.startswith(
            "application/json"
        ):
            response["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0"
            )
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
        return response


class PostLoginRedirectMiddleware:
    """If auth just occurred and a post-login target is stored, redirect once.

    Place after AuthenticationMiddleware.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            from django.shortcuts import redirect

            is_html_get = request.method == "GET" and "text/html" in request.headers.get(
                "Accept", ""
            )
            is_ajax = (
                request.headers.get("X-Requested-With") == "XMLHttpRequest"
                or request.path.startswith("/api/")
            )

            if (
                getattr(request, "user", None)
                and request.user.is_authenticated
                and is_html_get
                and not is_ajax
            ):
                target = request.session.pop(
                    "_next_after_login", None
                ) or request.session.pop("post_login_redirect", None)
                if (
                    target
                    and request.path != target
                    and getattr(response, "status_code", 200) in (200, 302)
                ):
                    return redirect(target)
        except Exception:
            pass
        return response


class QueryCountDebugMiddleware:
    """Log query count and execution time in development for performance monitoring."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not getattr(settings, "DEBUG", False):
            return self.get_response(request)

        # Reset queries
        from django.db import reset_queries

        reset_queries()

        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()

        # Count queries
        query_count = len(connection.queries)
        total_time = sum(float(q["time"]) for q in connection.queries)

        # Add headers for debugging
        response["X-DB-Query-Count"] = str(query_count)
        response["X-DB-Query-Time"] = f"{total_time:.4f}"
        response["X-Response-Time"] = f"{(end_time - start_time):.4f}"

        # Log if excessive
        if query_count > 50:
            print(
                f"⚠️  WARNING: {query_count} queries on {request.path} ({total_time:.4f}s)"
            )

        return response


class GzipCompressionMiddleware:
    """Add Content-Encoding hint for upstream compression (nginx, etc.)"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Add Vary header for cache optimization
        if "Accept-Encoding" not in response.get("Vary", ""):
            vary = response.get("Vary", "")
            response["Vary"] = f"{vary}, Accept-Encoding" if vary else "Accept-Encoding"

        return response


class ContentSecurityPolicyMiddleware:
    """Attach Content-Security-Policy headers for production hardening."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if getattr(settings, "CSP_ENFORCE", False):
            policy = getattr(settings, "CSP_POLICY", "").strip()
            if policy:
                if getattr(settings, "CSP_REPORT_ONLY", False):
                    response["Content-Security-Policy-Report-Only"] = policy
                else:
                    response["Content-Security-Policy"] = policy

        return response
