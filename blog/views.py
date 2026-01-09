from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse,HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.translation import get_language
from .models import (
    Article, Category, HomepageSEO, 
    NewsletterSubscriber, ContactMessage,
    CookieConsent, CookiePolicy
)


def get_seo_context():
    """Anasayfa SEO verilerini getir"""
    homepage_seo = HomepageSEO.objects.filter(is_active=True).first()
    cookie_consent = CookieConsent.objects.filter(is_active=True).first()
    return {
        'seo': homepage_seo,
        'cookie_consent': cookie_consent,
    }


def home(request):
    """Anasayfa"""
    # Öne çıkan makaleler
    featured_articles = Article.objects.filter(
        is_published=True, 
        is_featured=True
    ).select_related('category').order_by('-published_date')[:3]
    
    # Kategoriler
    categories = Category.objects.all()[:4]
    
    # SEO context
    context = get_seo_context()
    context.update({
        'featured_articles': featured_articles,
        'categories': categories,
        'page_title': 'Ana Sayfa',
    })
    
    return render(request, 'blog/home.html', context)


def blog_list(request):
    """Tüm makaleler listesi"""
    articles = Article.objects.filter(
        is_published=True
    ).select_related('category').order_by('-published_date')
    
    # Sayfalama
    paginator = Paginator(articles, 9)  # Sayfa başına 9 makale
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'page_title': 'Tüm Yazılar - EdebAi',
        'meta_description': 'Yapay zeka, prompt engineering ve dijital üretkenlik üzerine tüm makalelerimiz.',
    }
    
    return render(request, 'blog/blog_list.html', context)


def article_detail(request, slug):
    """Makale detay sayfası"""
    article = get_object_or_404(
        Article.objects.select_related('category').prefetch_related(
            'paragraphs', 'images'
        ),
        slug=slug,
        is_published=True
    )
    
    # Görüntülenme sayısını artır
    article.increment_view_count()
    
    # Paragrafları ve görselleri birleştir
    content_items = []
    paragraphs = article.paragraphs.all()
    
    for paragraph in paragraphs:
        content_items.append({
            'type': 'paragraph',
            'data': paragraph
        })
        
        # Bu paragraftan sonra gelen görseller
        following_images = article.images.filter(after_paragraph=paragraph)
        for image in following_images:
            content_items.append({
                'type': 'image',
                'data': image
            })
    
    # Belirli bir paragrafla ilişkilendirilmemiş görseller (sırasına göre)
    unlinked_images = article.images.filter(after_paragraph__isnull=True)
    for image in unlinked_images:
        content_items.append({
            'type': 'image',
            'data': image
        })
    
    # İlgili makaleler
    related_articles = Article.objects.filter(
        category=article.category,
        is_published=True
    ).exclude(id=article.id).order_by('-published_date')[:3]
    
    context = {
        'article': article,
        'content_items': content_items,
        'related_articles': related_articles,
        'page_title': article.meta_title or article.title,
    }
    
    return render(request, 'blog/article_detail.html', context)


def category_list(request):
    """Kategoriler sayfası"""
    categories = Category.objects.all()
    
    # Her kategori için makaleleri getir
    categories_with_articles = []
    for category in categories:
        articles = Article.objects.filter(
            category=category,
            is_published=True
        ).order_by('-published_date')[:3]
        
        categories_with_articles.append({
            'category': category,
            'articles': articles
        })
    
    context = {
        'categories_with_articles': categories_with_articles,
        'page_title': 'Kategoriler - EdebAi',
        'meta_description': 'Yapay zeka, prompt engineering, dijital üretkenlik ve etik AI kategorilerindeki makaleler.',
    }
    
    return render(request, 'blog/categories.html', context)


def category_detail(request, slug):
    """Kategori detay sayfası"""
    category = get_object_or_404(Category, slug=slug)
    
    articles = Article.objects.filter(
        category=category,
        is_published=True
    ).order_by('-published_date')
    
    # Sayfalama
    paginator = Paginator(articles, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
        'page_title': f'{category.name} - EdebAi',
        'meta_description': category.description or f'{category.name} kategorisindeki tüm makaleler.',
    }
    
    return render(request, 'blog/category_detail.html', context)


def about(request):
    """Hakkında sayfası"""
    context = {
        'page_title': 'Hakkında - EdebAi',
        'meta_description': 'EdebAi, yapay zeka ve edebiyatın buluştuğu noktada kaliteli içerikler üreten bir platformdur.',
    }
    return render(request, 'blog/about.html', context)


def contact(request):
    """İletişim sayfası"""
    context = {
        'page_title': 'İletişim - EdebAi',
        'meta_description': 'EdebAi ile iletişime geçin. Sorularınız, önerileriniz ve iş birliği teklifleriniz için bize ulaşın.',
    }
    return render(request, 'blog/contact.html', context)


@require_POST
def newsletter_subscribe(request):
    """Bülten aboneliği (AJAX)"""
    email = request.POST.get('email', '').strip()
    
    if not email:
        return JsonResponse({
            'success': False,
            'message': 'E-posta adresi gereklidir.'
        }, status=400)
    
    # E-posta zaten kayıtlı mı?
    subscriber, created = NewsletterSubscriber.objects.get_or_create(
        email=email,
        defaults={'is_active': True}
    )
    
    if not created:
        if subscriber.is_active:
            return JsonResponse({
                'success': False,
                'message': 'Bu e-posta adresi zaten kayıtlı.'
            }, status=400)
        else:
            # Pasif aboneyi tekrar aktif et
            subscriber.is_active = True
            subscriber.save()
            return JsonResponse({
                'success': True,
                'message': 'Aboneliğiniz yeniden aktif edildi!'
            })
    
    return JsonResponse({
        'success': True,
        'message': 'Teşekkürler! Bültene başarıyla abone oldunuz.'
    })


@require_POST
def contact_submit(request):
    """İletişim formu gönderimi (AJAX)"""
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    message = request.POST.get('message', '').strip()
    
    # Validasyon
    if not all([name, email, message]):
        return JsonResponse({
            'success': False,
            'message': 'Lütfen tüm alanları doldurun.'
        }, status=400)
    
    # Mesajı kaydet
    ContactMessage.objects.create(
        name=name,
        email=email,
        message=message
    )
    
    return JsonResponse({
        'success': True,
        'message': 'Mesajınız başarıyla gönderildi. En kısa sürede size dönüş yapacağız.'
    })


def search(request):
    """Arama sayfası"""
    query = request.GET.get('q', '').strip()
    
    if query:
        articles = Article.objects.filter(
            Q(title__icontains=query) | 
            Q(title_en__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(excerpt_en__icontains=query) |
            Q(meta_description__icontains=query),
            is_published=True
        ).select_related('category').order_by('-published_date')
        
        # Sayfalama
        paginator = Paginator(articles, 9)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
    else:
        page_obj = None
    
    context = get_seo_context()
    context.update({
        'query': query,
        'page_obj': page_obj,
        'page_title': f'Arama: {query}' if query else 'Arama - EdebAi',
        'meta_description': f'{query} ile ilgili arama sonuçları.' if query else 'EdebAi\'de arama yapın.',
    })
    
    return render(request, 'blog/search.html', context)


def cookie_policy(request):
    """Çerez politikası sayfası"""
    policy = CookiePolicy.objects.filter(is_active=True).first()
    
    if not policy:
        # Varsayılan içerik
        policy = type('obj', (object,), {
            'title_tr': 'Çerez Politikası',
            'title_en': 'Cookie Policy',
            'content_tr': 'Çerez politikası içeriği henüz eklenmemiş.',
            'content_en': 'Cookie policy content not yet added.',
            'last_updated': None,
            'meta_description_tr': '',
            'meta_description_en': '',
        })()
    
    context = get_seo_context()
    context.update({
        'policy': policy,
        'page_title': policy.title_tr if get_language() == 'tr' else policy.title_en,
        'meta_description': policy.meta_description_tr or 'EdebAi çerez politikası',
    })
    
    return render(request, 'blog/cookie_policy.html', context)


def set_language(request, language):
    """Dil değiştirme"""
    if language in ['tr', 'en']:
        response = redirect(request.META.get('HTTP_REFERER', '/'))
        response.set_cookie('language', language, max_age=365*24*60*60)  # 1 yıl
        if hasattr(request, 'session'):
            request.session['language'] = language
        return response
    return redirect('/')


def robots_txt(request):
    content = """User-agent: *
Disallow: /admin/

Sitemap: https://edebai.com.tr/sitemap.xml
"""
    return HttpResponse(content, content_type="text/plain")