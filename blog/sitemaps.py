from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Article, Category


class ArticleSitemap(Sitemap):
    """Makale sitemap'i"""
    changefreq = "weekly"
    priority = 0.9
    
    def items(self):
        return Article.objects.filter(is_published=True, noindex=False).order_by('-published_date')
    
    def lastmod(self, obj):
        return obj.updated_at
    
    def location(self, obj):
        return obj.get_absolute_url()


class CategorySitemap(Sitemap):
    """Kategori sitemap'i"""
    changefreq = "weekly"
    priority = 0.7
    
    def items(self):
        return Category.objects.all()
    
    def location(self, obj):
        return reverse('blog:category_detail', args=[obj.slug])


class StaticViewSitemap(Sitemap):
    """Statik sayfalar sitemap'i"""
    priority = 0.5
    changefreq = 'monthly'
    
    def items(self):
        return ['blog:home', 'blog:blog_list', 'blog:category_list', 'blog:about', 'blog:contact']
    
    def location(self, item):
        return reverse(item)