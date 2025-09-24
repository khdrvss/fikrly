from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Company, Review


class CompanySitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Company.objects.all().order_by('id')

    def lastmod(self, obj: Company):
        return None

    def location(self, obj: Company):
        return reverse('company_detail', kwargs={'pk': obj.pk})


class StaticSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.5

    def items(self):
        return ['index', 'business_list', 'category_browse', 'review_submission', 'privacy_policy']

    def location(self, item):
        return reverse(item)
