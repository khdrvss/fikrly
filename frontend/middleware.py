from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.db import connection
import time


class NoCacheMiddleware(MiddlewareMixin):
    """Disable client-side caching in development for HTML/JSON responses."""

    def process_response(self, request, response):
        if getattr(settings, "DEBUG", False):
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

            if getattr(request, "user", None) and request.user.is_authenticated:
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
        if not getattr(settings, 'DEBUG', False):
            return self.get_response(request)
        
        # Reset queries
        from django.db import reset_queries
        reset_queries()
        
        start_time = time.time()
        response = self.get_response(request)
        end_time = time.time()
        
        # Count queries
        query_count = len(connection.queries)
        total_time = sum(float(q['time']) for q in connection.queries)
        
        # Add headers for debugging
        response['X-DB-Query-Count'] = str(query_count)
        response['X-DB-Query-Time'] = f"{total_time:.4f}"
        response['X-Response-Time'] = f"{(end_time - start_time):.4f}"
        
        # Log if excessive
        if query_count > 50:
            print(f"⚠️  WARNING: {query_count} queries on {request.path} ({total_time:.4f}s)")
        
        return response


class GzipCompressionMiddleware:
    """Add Content-Encoding hint for upstream compression (nginx, etc.)"""
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Add Vary header for cache optimization
        if 'Accept-Encoding' not in response.get('Vary', ''):
            vary = response.get('Vary', '')
            response['Vary'] = f"{vary}, Accept-Encoding" if vary else "Accept-Encoding"
        
        return response
