"""
Custom admin site with enhanced dashboard.
"""

from django.contrib.admin import AdminSite
from frontend.admin_dashboard import admin_dashboard


class FikrlyAdminSite(AdminSite):
    site_header = "Fikrly Admin"
    site_title = "Fikrly Admin"
    index_title = "Boshqaruv paneli"

    def index(self, request, extra_context=None):
        """Override index view with custom dashboard."""
        return admin_dashboard(request)


# Create custom admin site instance
admin_site = FikrlyAdminSite(name="admin")
