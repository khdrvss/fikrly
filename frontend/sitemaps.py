from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Company, BusinessCategory
from .visibility import public_companies_queryset, visible_business_categories


class CategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        return visible_business_categories(BusinessCategory.objects.all()).order_by("id")

    def location(self, obj: BusinessCategory):
        return obj.get_absolute_url()


class CompanySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9
    protocol = "https"

    def items(self):
        return public_companies_queryset().order_by("id")

    def lastmod(self, obj: Company):
        return None

    def location(self, obj: Company):
        return reverse("company_detail", kwargs={"pk": obj.pk})


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5
    protocol = "https"

    def items(self):
        return [
            "index",
            "business_list",
            "category_browse",
            "review_submission",
            "privacy_policy",
            "terms_of_service",
            "community_guidelines",
            "contact_us",
        ]

    def location(self, item):
        return reverse(item)
