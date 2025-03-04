"""
URL configuration for tour_desk project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.decorators.cache import cache_page

from sitetour.sitemaps import PostSitemap
import sitetour.views

handler404 = sitetour.views.page_not_found_view


sitemaps = {
	'posts':PostSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('sitetour.urls')),
    path('users/', include('users.urls',namespace='users')),
    path('social-auth/', include('social_django.urls',namespace='social')),
    path('sitemap.xml',cache_page(86400)(sitemap),{'sitemaps':sitemaps},name='dlango.contrib.sitemaps.views.sitemaps'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns = urlpatterns + [path('__debug__/', include('debug_toolbar.urls'))] if settings.DEBUG else urlpatterns
