"""
Public visibility helpers.

Rules
------
A company is publicly visible when ALL of the following are true:
1. company.is_active is True
2. company.category_fk is NULL  OR  company.category_fk.is_active is True

A BusinessCategory is publicly visible when:
   category.is_active is True
"""

from django.core.cache import cache
from django.db.models import QuerySet

from .models import BusinessCategory, Company


CATEGORIES_CACHE_KEY = "visible_business_categories"
CATEGORIES_CACHE_TTL = 60 * 15  # 15 minutes


def get_cached_categories() -> QuerySet[BusinessCategory]:
    """Get visible business categories with caching."""
    cached = cache.get(CATEGORIES_CACHE_KEY)
    if cached is not None:
        return cached
    
    categories = visible_business_categories(BusinessCategory.objects.all())
    cache.set(CATEGORIES_CACHE_KEY, categories, CATEGORIES_CACHE_TTL)
    return categories


def invalidate_categories_cache() -> None:
    """Call this when categories are modified."""
    cache.delete(CATEGORIES_CACHE_KEY)


# ---------------------------------------------------------------------------
# Core querysets
# ---------------------------------------------------------------------------

def public_companies_queryset() -> QuerySet[Company]:
    """Return all companies that should be shown to anonymous site visitors."""
    return Company.objects.filter(
        is_active=True,
    ).exclude(
        category_fk__is_active=False,  # exclude companies whose FK category is hidden
    )


def visible_business_categories(
    queryset: QuerySet[BusinessCategory] | None = None,
) -> QuerySet[BusinessCategory]:
    """Filter a BusinessCategory queryset to only active (visible) ones."""
    qs = queryset if queryset is not None else BusinessCategory.objects.all()
    return qs.filter(is_active=True)


# ---------------------------------------------------------------------------
# Per-object helpers (used in detail / report views)
# ---------------------------------------------------------------------------

def is_company_publicly_visible(company: Company) -> bool:
    """Return True when a company should be accessible on public pages."""
    if not company.is_active:
        return False
    # If company has a category FK, check it too
    if company.category_fk_id:
        # Use cached _state if already fetched, otherwise hit DB
        try:
            if not company.category_fk.is_active:
                return False
        except BusinessCategory.DoesNotExist:
            pass
    return True