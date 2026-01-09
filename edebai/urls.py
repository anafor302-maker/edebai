from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from blog.sitemaps import ArticleSitemap, StaticViewSitemap

sitemaps = {
    'articles': ArticleSitemap,
    'static': StaticViewSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blog.urls')),

    # Sitemap (template YOK, Django üretir)
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
