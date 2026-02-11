from django.conf import settings

def google_analytics(request):
    """
    Makes the Google Analytics Measurement ID available in all templates.
    """
    return {
        "GA_MEASUREMENT_ID": getattr(settings, "GA_MEASUREMENT_ID", "")
    }
