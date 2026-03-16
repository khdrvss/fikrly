"""Simple API views with versioning support."""
import json
from django.db import models
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Avg, Count
from frontend.models import Company, BusinessCategory, Review
from frontend.visibility import public_companies_queryset, visible_business_categories
from frontend.cache_utils import get_safe_limit_param, get_safe_pagination_param


API_VERSIONS = {
    "v1": {
        "companies": "v1_companies",
        "categories": "v1_categories",
        "company_detail": "v1_company_detail",
    },
}

ALLOWED_ORIGINS = [
    "https://fikrly.uz",
    "https://www.fikrly.uz",
    "http://localhost:3000",
    "http://localhost:8000",
]


def add_cors_headers(response, request):
    """Add CORS headers to response."""
    origin = request.headers.get("Origin", "")
    if origin in ALLOWED_ORIGINS:
        response["Access-Control-Allow-Origin"] = origin
    response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Accept-Language"
    response["Access-Control-Max-Age"] = "3600"
    return response


def options_handler(request):
    """Handle CORS preflight requests."""
    response = HttpResponse(status=204)
    return add_cors_headers(response, request)


def get_api_version(request):
    """Extract API version from Accept header or query param."""
    accept = request.headers.get("Accept", "")
    if "version=v1" in accept:
        return "v1"
    if "version=v2" in accept:
        return "v2"
    return request.GET.get("api_version", "v1")


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def api_root(request):
    """API root endpoint with version info."""
    if request.method == "OPTIONS":
        return options_handler(request)
    
    version = get_api_version(request)
    response = JsonResponse({
        "api_version": version,
        "endpoints": {
            "companies": f"/api/{version}/companies/",
            "categories": f"/api/{version}/categories/",
            "health": "/health/",
        },
    })
    return add_cors_headers(response, request)


@require_http_methods(["GET", "OPTIONS"])
def v1_companies(request):
    """List companies with basic info."""
    if request.method == "OPTIONS":
        return options_handler(request)
    
    limit = get_safe_limit_param(request, "limit", 20, 50)
    page = get_safe_pagination_param(request)
    page = get_safe_pagination_param(request)
    
    companies = (
        public_companies_queryset()
        .select_related("category_fk")
        .only("id", "name", "slug", "city", "rating", "review_count", "is_verified", "category_fk__name", "category_fk__slug", "image_400", "image_url")
    )
    
    from django.core.paginator import Paginator
    paginator = Paginator(companies, limit)
    page_obj = paginator.get_page(page)
    
    return JsonResponse({
        "companies": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "city": c.city,
                "rating": float(c.rating) if c.rating else None,
                "review_count": c.review_count,
                "is_verified": c.is_verified,
                "category": c.category_fk.name if c.category_fk else None,
                "image": c.image_400_url if c.image_400 else c.image_url,
            }
            for c in page_obj
        ],
        "pagination": {
            "page": page_obj.number,
            "total_pages": paginator.num_pages,
            "total_count": paginator.count,
            "has_next": page_obj.has_next(),
            "has_prev": page_obj.has_previous(),
        },
    })
    return add_cors_headers(response, request)


@require_http_methods(["GET", "OPTIONS"])
def v1_categories(request):
    """List business categories."""
    if request.method == "OPTIONS":
        return options_handler(request)
    
    categories = (
        visible_business_categories(BusinessCategory.objects.all())
        .annotate(company_count=Count("companies", filter=Q(companies__is_active=True)))
        .order_by("-company_count")[:50]
    )
    
    return JsonResponse({
        "categories": [
            {
                "id": c.id,
                "name": c.name,
                "slug": c.slug,
                "color": c.color,
                "company_count": c.company_count,
            }
            for c in categories
        ],
    })
    return add_cors_headers(response, request)


@require_http_methods(["GET", "OPTIONS"])
def v1_company_detail(request, slug):
    """Get company detail with reviews."""
    if request.method == "OPTIONS":
        return options_handler(request)
    """Get company detail with reviews."""
    company = public_companies_queryset().filter(slug=slug).select_related("category_fk").first()
    if not company:
        return JsonResponse({"error": "Company not found"}, status=404)
    
    reviews_limit = get_safe_limit_param(request, "reviews_limit", 5, 20)
    reviews = company.reviews.filter(is_approved=True).order_by("-created_at")[:reviews_limit]
    
    return JsonResponse({
        "company": {
            "id": company.id,
            "name": company.name,
            "slug": company.slug,
            "description": company.description,
            "city": company.city,
            "address": company.address,
            "phone": company.phone_public,
            "website": company.website,
            "rating": float(company.rating) if company.rating else None,
            "review_count": company.review_count,
            "is_verified": company.is_verified,
            "is_claimed": company.is_claimed,
            "category": company.category_fk.name if company.category_fk else None,
            "image": company.image_800_url if company.image_800 else company.image_url,
            "logo": company.logo.url if company.logo else company.logo_url,
        },
        "reviews": [
            {
                "id": r.id,
                "rating": r.rating,
                "text": r.text[:500],
                "user_name": r.user_name,
                "created_at": r.created_at.isoformat(),
            }
            for r in reviews
        ],
    })
    return add_cors_headers(response, request)
