from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class NoCacheMiddleware(MiddlewareMixin):
    """Disable client-side caching in development for HTML/JSON responses."""

    def process_response(self, request, response):
        if getattr(settings, 'DEBUG', False):
            content_type = response.get('Content-Type', '')
            if content_type.startswith('text/html') or content_type.startswith('application/json'):
                response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'
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
            if getattr(request, 'user', None) and request.user.is_authenticated:
                target = request.session.pop('_next_after_login', None) or request.session.pop('post_login_redirect', None)
                if target and request.path != target and getattr(response, 'status_code', 200) in (200, 302):
                    return redirect(target)
        except Exception:
            pass
        return response
