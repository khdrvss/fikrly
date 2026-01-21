"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from frontend.sitemaps import CompanySitemap, StaticSitemap, CategorySitemap
from frontend.views import robots_txt, bing_site_auth, favicon_file
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import TemplateView

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("BingSiteAuth.xml", bing_site_auth, name="bing_site_auth"),
    path(
        "sitemap.xml",
        sitemap,
        {
            "sitemaps": {
                "companies": CompanySitemap,
                "categories": CategorySitemap,
                "static": StaticSitemap,
            }
        },
        name="sitemap",
    ),
    path("favicon.ico", favicon_file, name="favicon"),
    # Service Worker for PWA
    path(
        "service-worker.js",
        TemplateView.as_view(
            template_name="service-worker.js",
            content_type="application/javascript"
        ),
        name="service_worker"
    ),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("accounts/", include("allauth.urls")),
    path("", include("frontend.urls")),
    prefix_default_language=False,
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Silk profiler - only in development or when explicitly enabled
SILK_ENABLED = getattr(settings, 'SILK_ENABLED', False)
if SILK_ENABLED:
    urlpatterns += [
        path("silk/", include("silk.urls", namespace="silk")),
    ]
