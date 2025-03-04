from django.contrib.sitemaps import Sitemap
from .models import Tour
from django.utils import timezone


class PostSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        return Tour.objects.all()

    def lastmod(self, obj):
        return timezone.now()
