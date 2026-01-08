from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Category, HomepageSEO, Article, ArticleParagraph, 
    ArticleImage, NewsletterSubscriber, ContactMessage,
    CookieConsent, CookiePolicy
)


class ArticleParagraphInline(admin.TabularInline):
    model = ArticleParagraph
    extra = 1
    fields = ('order', 'paragraph_type', 'heading_text', 'heading_text_en', 'content', 'content_en', 'code_language')


class ArticleImageInline(admin.TabularInline):
    model = ArticleImage
    extra = 1
    fields = ('order', 'image', 'alt_text', 'caption', 'after_paragraph')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 200px; max-height: 150px;" />', obj.image.url)
        return '-'
    image_preview.short_description = 'Önizleme'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon', 'article_count', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def article_count(self, obj):
        return obj.get_article_count()
    article_count.short_description = 'Makale Sayısı'


@admin.register(HomepageSEO)
class HomepageSEOAdmin(admin.ModelAdmin):
    list_display = ('meta_title', 'is_active', 'updated_at')
    list_filter = ('is_active',)
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('is_active', 'canonical_url')
        }),
        ('Arama Motoru Optimizasyonu', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords'),
            'description': 'Google arama sonuçlarında görünecek bilgiler'
        }),
        ('Sosyal Medya (Open Graph)', {
            'fields': ('og_title', 'og_description', 'og_image'),
            'classes': ('collapse',),
            'description': 'Facebook, LinkedIn vb. platformlarda paylaşım görünümü'
        }),
        ('Twitter', {
            'fields': ('twitter_card_type',),
            'classes': ('collapse',)
        }),
        ('Gelişmiş', {
            'fields': ('structured_data',),
            'classes': ('collapse',),
            'description': 'JSON-LD formatında yapılandırılmış veri'
        })
    )


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author_name', 'is_published', 'is_featured', 
                    'published_date', 'view_count', 'thumbnail_preview')
    list_filter = ('is_published', 'is_featured', 'category', 'created_at')
    list_editable = ('is_published', 'is_featured')
    search_fields = ('title', 'excerpt', 'meta_description', 'author_name')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_date'
    readonly_fields = ('view_count', 'created_at', 'updated_at', 'thumbnail_preview')
    
    inlines = [ArticleParagraphInline, ArticleImageInline]
    
    fieldsets = (
        ('Temel Bilgiler', {
            'fields': ('title', 'title_en', 'slug', 'category', 'language', 'author_name', 'author_bio')
        }),
        ('İçerik', {
            'fields': ('excerpt', 'excerpt_en', 'thumbnail', 'thumbnail_alt', 'reading_time'),
            'description': 'Paragraflar ve ek görseller aşağıdaki bölümlerden eklenecek'
        }),
        ('Durum', {
            'fields': ('is_published', 'is_featured', 'published_date', 'noindex')
        }),
        ('SEO - Türkçe', {
            'fields': ('meta_title', 'meta_description', 'meta_keywords', 'canonical_url'),
            'classes': ('collapse',),
            'description': 'Google arama sonuçları için optimizasyon (Türkçe)'
        }),
        ('SEO - English', {
            'fields': ('meta_title_en', 'meta_description_en', 'meta_keywords_en'),
            'classes': ('collapse',),
            'description': 'Google search results optimization (English)'
        }),
        ('SEO - Sosyal Medya', {
            'fields': ('og_title', 'og_description', 'og_image', 'twitter_card_type'),
            'classes': ('collapse',)
        }),
        ('İstatistikler', {
            'fields': ('view_count', 'created_at', 'updated_at', 'thumbnail_preview'),
            'classes': ('collapse',)
        })
    )
    
    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px; border-radius: 8px;" />',
                obj.thumbnail.url
            )
        return '-'
    thumbnail_preview.short_description = 'Kapak Görseli Önizleme'
    
    def save_model(self, request, obj, form, change):
        # Yayına alınırken tarih yoksa otomatik ekle
        if obj.is_published and not obj.published_date:
            from django.utils import timezone
            obj.published_date = timezone.now()
        super().save_model(request, obj, form, change)




@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ('email', 'is_active', 'subscribed_at')
    list_filter = ('is_active', 'subscribed_at')
    search_fields = ('email',)
    list_editable = ('is_active',)
    date_hierarchy = 'subscribed_at'
    
    actions = ['activate_subscribers', 'deactivate_subscribers']
    
    def activate_subscribers(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} abone aktif edildi.')
    activate_subscribers.short_description = 'Seçili aboneleri aktif et'
    
    def deactivate_subscribers(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} abone pasif edildi.')
    deactivate_subscribers.short_description = 'Seçili aboneleri pasif et'


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at', 'is_read', 'message_preview')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    list_editable = ('is_read',)
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def message_preview(self, obj):
        return obj.message[:80] + '...' if len(obj.message) > 80 else obj.message
    message_preview.short_description = 'Mesaj Önizleme'
    
    def mark_as_read(self, request, queryset):
        count = queryset.update(is_read=True)
        self.message_user(request, f'{count} mesaj okundu olarak işaretlendi.')
    mark_as_read.short_description = 'Okundu olarak işaretle'
    
    def mark_as_unread(self, request, queryset):
        count = queryset.update(is_read=False)
        self.message_user(request, f'{count} mesaj okunmadı olarak işaretlendi.')
    mark_as_unread.short_description = 'Okunmadı olarak işaretle'


# Admin site özelleştirmeleri
admin.site.site_header = "EdebAi Yönetim Paneli"
admin.site.site_title = "EdebAi Admin"
admin.site.index_title = "Hoş Geldiniz"


@admin.register(CookieConsent)
class CookieConsentAdmin(admin.ModelAdmin):
    list_display = ('is_active', 'message_preview_tr', 'message_preview_en')
    list_display_links = ('message_preview_tr',)
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Durum', {
            'fields': ('is_active',)
        }),
        ('Türkçe İçerik', {
            'fields': ('message_tr', 'button_text_tr', 'policy_link_text_tr')
        }),
        ('English Content', {
            'fields': ('message_en', 'button_text_en', 'policy_link_text_en'),
            'classes': ('collapse',)
        })
    )
    
    def message_preview_tr(self, obj):
        return obj.message_tr[:60] + '...' if len(obj.message_tr) > 60 else obj.message_tr
    message_preview_tr.short_description = 'Mesaj (TR)'
    
    def message_preview_en(self, obj):
        return obj.message_en[:60] + '...' if len(obj.message_en) > 60 else obj.message_en
    message_preview_en.short_description = 'Message (EN)'


@admin.register(CookiePolicy)
class CookiePolicyAdmin(admin.ModelAdmin):
    list_display = ('title_tr', 'title_en', 'last_updated', 'is_active')
    list_editable = ('is_active',)
    
    fieldsets = (
        ('Durum', {
            'fields': ('is_active',)
        }),
        ('Türkçe İçerik', {
            'fields': ('title_tr', 'content_tr', 'meta_description_tr')
        }),
        ('English Content', {
            'fields': ('title_en', 'content_en', 'meta_description_en'),
            'classes': ('collapse',)
        })
    )