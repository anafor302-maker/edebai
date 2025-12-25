from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import MinLengthValidator


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Kategori Adı")
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    icon = models.CharField(max_length=10, default="📝", verbose_name="Emoji İkon")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    order = models.IntegerField(default=0, verbose_name="Sıralama")
    
    class Meta:
        verbose_name = "Kategori"
        verbose_name_plural = "Kategoriler"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    def get_article_count(self):
        return self.articles.filter(is_published=True).count()


class SEOMetadata(models.Model):
    """Tekrar kullanılabilir SEO metadata modeli"""
    meta_title = models.CharField(
        max_length=60, 
        verbose_name="Meta Başlık",
        help_text="Google'da görünecek başlık (60 karakter önerilir)"
    )
    meta_description = models.CharField(
        max_length=160, 
        verbose_name="Meta Açıklama",
        help_text="Google'da görünecek açıklama (160 karakter önerilir)",
        validators=[MinLengthValidator(50)]
    )
    meta_keywords = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Anahtar Kelimeler",
        help_text="Virgülle ayrılmış anahtar kelimeler"
    )
    og_title = models.CharField(
        max_length=95, 
        blank=True,
        verbose_name="Open Graph Başlık",
        help_text="Sosyal medyada paylaşıldığında görünecek başlık"
    )
    og_description = models.CharField(
        max_length=200, 
        blank=True,
        verbose_name="Open Graph Açıklama"
    )
    og_image = models.ImageField(
        upload_to='seo/og_images/', 
        blank=True, 
        null=True,
        verbose_name="Open Graph Görseli",
        help_text="1200x630px önerilir"
    )
    twitter_card_type = models.CharField(
        max_length=50, 
        default="summary_large_image",
        choices=[
            ('summary', 'Summary'),
            ('summary_large_image', 'Summary Large Image'),
        ],
        verbose_name="Twitter Card Tipi"
    )
    
    class Meta:
        abstract = True


class HomepageSEO(SEOMetadata):
    """Anasayfa için özel SEO ayarları"""
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    canonical_url = models.URLField(blank=True, verbose_name="Canonical URL")
    structured_data = models.JSONField(
        blank=True, 
        null=True,
        verbose_name="Yapılandırılmış Veri (JSON-LD)",
        help_text="Organization, WebSite vb. schema.org verileri"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Anasayfa SEO"
        verbose_name_plural = "Anasayfa SEO"
    
    def __str__(self):
        return f"Anasayfa SEO - {self.meta_title}"
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Sadece bir tane aktif anasayfa SEO olabilir
            HomepageSEO.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class Article(SEOMetadata):
    """Makale modeli - SEO özellikli"""
    title = models.CharField(max_length=200, verbose_name="Başlık (TR)")
    title_en = models.CharField(max_length=200, blank=True, verbose_name="Başlık (EN)")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(
        Category, 
        on_delete=models.SET_NULL, 
        null=True,
        related_name='articles',
        verbose_name="Kategori"
    )
    
    # Dil ayarları
    LANGUAGE_CHOICES = [
        ('tr', 'Türkçe'),
        ('en', 'English'),
        ('both', 'İki Dilde'),
    ]
    language = models.CharField(
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='both',
        verbose_name="Dil"
    )
    
    # Özet bilgiler
    excerpt = models.TextField(
        max_length=300,
        verbose_name="Özet (TR)",
        help_text="Kart görünümlerinde gösterilecek kısa özet"
    )
    excerpt_en = models.TextField(
        max_length=300,
        blank=True,
        verbose_name="Özet (EN)",
        help_text="İngilizce kısa özet"
    )
    
    # Görsel
    thumbnail = models.ImageField(
        upload_to='articles/thumbnails/%Y/%m/',
        verbose_name="Kapak Görseli",
        help_text="Ana görsel - 1200x800px önerilir"
    )
    thumbnail_alt = models.CharField(
        max_length=200,
        verbose_name="Görsel Alt Metni",
        help_text="SEO için görsel açıklaması"
    )
    
    # Yazar bilgileri
    author_name = models.CharField(max_length=100, verbose_name="Yazar Adı")
    author_bio = models.TextField(blank=True, verbose_name="Yazar Biyografisi")
    
    # Okuma ve tarih bilgileri
    reading_time = models.IntegerField(
        default=5,
        verbose_name="Okuma Süresi (dakika)",
        help_text="Tahmini okuma süresi"
    )
    published_date = models.DateTimeField(
        blank=True, 
        null=True,
        verbose_name="Yayın Tarihi"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturma")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncelleme")
    
    # Durum
    is_published = models.BooleanField(default=False, verbose_name="Yayında")
    is_featured = models.BooleanField(default=False, verbose_name="Öne Çıkan")
    
    # SEO - Ek alanlar
    canonical_url = models.URLField(blank=True, verbose_name="Canonical URL")
    noindex = models.BooleanField(
        default=False,
        verbose_name="Noindex",
        help_text="Arama motorlarından gizle"
    )
    
    # SEO için İngilizce metadata
    meta_title_en = models.CharField(
        max_length=60, 
        blank=True,
        verbose_name="Meta Başlık (EN)"
    )
    meta_description_en = models.CharField(
        max_length=160, 
        blank=True,
        verbose_name="Meta Açıklama (EN)"
    )
    meta_keywords_en = models.CharField(
        max_length=255, 
        blank=True,
        verbose_name="Anahtar Kelimeler (EN)"
    )
    
    # İstatistikler
    view_count = models.IntegerField(default=0, verbose_name="Görüntülenme")
    
    class Meta:
        verbose_name = "Makale"
        verbose_name_plural = "Makaleler"
        ordering = ['-published_date', '-created_at']
        indexes = [
            models.Index(fields=['-published_date', 'is_published']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        
        # Meta title ve og_title otomatik doldurma
        if not self.meta_title:
            self.meta_title = self.title[:60]
        if not self.og_title:
            self.og_title = self.title[:95]
        if not self.og_description:
            self.og_description = self.excerpt[:200]
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})
    
    def get_title(self, language='tr'):
        """Dile göre başlık döndür"""
        if language == 'en' and self.title_en:
            return self.title_en
        return self.title
    
    def get_excerpt(self, language='tr'):
        """Dile göre özet döndür"""
        if language == 'en' and self.excerpt_en:
            return self.excerpt_en
        return self.excerpt
    
    def get_meta_title(self, language='tr'):
        """Dile göre meta title döndür"""
        if language == 'en' and self.meta_title_en:
            return self.meta_title_en
        return self.meta_title
    
    def get_meta_description(self, language='tr'):
        """Dile göre meta description döndür"""
        if language == 'en' and self.meta_description_en:
            return self.meta_description_en
        return self.meta_description
    
    def increment_view_count(self):
        self.view_count += 1
        self.save(update_fields=['view_count'])


class ArticleParagraph(models.Model):
    """Makale paragrafları"""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='paragraphs',
        verbose_name="Makale"
    )
    order = models.IntegerField(default=0, verbose_name="Sıra")
    
    PARAGRAPH_TYPES = [
        ('text', 'Normal Paragraf'),
        ('heading', 'Alt Başlık'),
        ('quote', 'Alıntı'),
        ('code', 'Kod Bloğu'),
    ]
    
    paragraph_type = models.CharField(
        max_length=20,
        choices=PARAGRAPH_TYPES,
        default='text',
        verbose_name="Paragraf Tipi"
    )
    
    content = models.TextField(verbose_name="İçerik (TR)")
    content_en = models.TextField(blank=True, verbose_name="İçerik (EN)")
    
    # Opsiyonel başlık (heading tipi için)
    heading_text = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Alt Başlık (TR)",
        help_text="Sadece 'Alt Başlık' tipi için"
    )
    heading_text_en = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Alt Başlık (EN)"
    )
    
    # Kod bloğu için dil seçeneği
    code_language = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="Kod Dili",
        help_text="Örn: python, javascript, html"
    )
    
    class Meta:
        verbose_name = "Makale Paragrafı"
        verbose_name_plural = "Makale Paragrafları"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.article.title} - Paragraf {self.order}"
    
    def get_content(self, language='tr'):
        """Dile göre içerik döndür"""
        if language == 'en' and self.content_en:
            return self.content_en
        return self.content
    
    def get_heading(self, language='tr'):
        """Dile göre başlık döndür"""
        if language == 'en' and self.heading_text_en:
            return self.heading_text_en
        return self.heading_text


class ArticleImage(models.Model):
    """Makale içi görseller"""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="Makale"
    )
    image = models.ImageField(
        upload_to='articles/content_images/%Y/%m/',
        verbose_name="Görsel"
    )
    alt_text = models.CharField(
        max_length=200,
        verbose_name="Alt Metin",
        help_text="SEO için görsel açıklaması"
    )
    caption = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="Görsel Başlığı"
    )
    order = models.IntegerField(default=0, verbose_name="Sıra")
    
    # Paragraftan sonra gösterilecek mi?
    after_paragraph = models.ForeignKey(
        ArticleParagraph,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='following_images',
        verbose_name="Hangi Paragraftan Sonra",
        help_text="Boş bırakılırsa sırasına göre gösterilir"
    )
    
    class Meta:
        verbose_name = "Makale Görseli"
        verbose_name_plural = "Makale Görselleri"
        ordering = ['order']
    
    def __str__(self):
        return f"{self.article.title} - Görsel {self.order}"


class NewsletterSubscriber(models.Model):
    """Bülten aboneleri"""
    email = models.EmailField(unique=True, verbose_name="E-posta")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    subscribed_at = models.DateTimeField(auto_now_add=True, verbose_name="Kayıt Tarihi")
    
    class Meta:
        verbose_name = "Bülten Abonesi"
        verbose_name_plural = "Bülten Aboneleri"
        ordering = ['-subscribed_at']
    
    def __str__(self):
        return self.email


class ContactMessage(models.Model):
    """İletişim mesajları"""
    name = models.CharField(max_length=100, verbose_name="Ad Soyad")
    email = models.EmailField(verbose_name="E-posta")
    message = models.TextField(verbose_name="Mesaj")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Gönderilme")
    is_read = models.BooleanField(default=False, verbose_name="Okundu")
    
    class Meta:
        verbose_name = "İletişim Mesajı"
        verbose_name_plural = "İletişim Mesajları"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%d.%m.%Y')}"


class CookieConsent(models.Model):
    """Çerez politikası ayarları"""
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    message_tr = models.TextField(
        verbose_name="Mesaj (TR)",
        default="Bu web sitesi, deneyiminizi geliştirmek için çerezler kullanmaktadır."
    )
    message_en = models.TextField(
        verbose_name="Mesaj (EN)",
        default="This website uses cookies to improve your experience."
    )
    button_text_tr = models.CharField(
        max_length=50,
        default="Anladım",
        verbose_name="Buton Metni (TR)"
    )
    button_text_en = models.CharField(
        max_length=50,
        default="I Understand",
        verbose_name="Buton Metni (EN)"
    )
    policy_link_text_tr = models.CharField(
        max_length=50,
        default="Çerez Politikası",
        verbose_name="Politika Linki (TR)"
    )
    policy_link_text_en = models.CharField(
        max_length=50,
        default="Cookie Policy",
        verbose_name="Politika Linki (EN)"
    )
    
    class Meta:
        verbose_name = "Çerez Onayı Ayarları"
        verbose_name_plural = "Çerez Onayı Ayarları"
    
    def __str__(self):
        return "Çerez Onayı Ayarları"
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Sadece bir tane aktif olabilir
            CookieConsent.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)


class CookiePolicy(models.Model):
    """Çerez politikası içeriği"""
    title_tr = models.CharField(max_length=200, default="Çerez Politikası", verbose_name="Başlık (TR)")
    title_en = models.CharField(max_length=200, default="Cookie Policy", verbose_name="Başlık (EN)")
    content_tr = models.TextField(verbose_name="İçerik (TR)")
    content_en = models.TextField(verbose_name="İçerik (EN)")
    last_updated = models.DateField(auto_now=True, verbose_name="Son Güncelleme")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    
    # SEO
    meta_description_tr = models.CharField(max_length=160, blank=True, verbose_name="Meta Açıklama (TR)")
    meta_description_en = models.CharField(max_length=160, blank=True, verbose_name="Meta Açıklama (EN)")
    
    class Meta:
        verbose_name = "Çerez Politikası"
        verbose_name_plural = "Çerez Politikası"
    
    def __str__(self):
        return self.title_tr
    
    def save(self, *args, **kwargs):
        if self.is_active:
            CookiePolicy.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)