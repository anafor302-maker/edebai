from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Ana sayfalar
    path('', views.home, name='home'),
    path('blog/', views.blog_list, name='blog_list'),
    path('kategoriler/', views.category_list, name='category_list'),
    path('kategori/<slug:slug>/', views.category_detail, name='category_detail'),
    path('hakkinda/', views.about, name='about'),
    path('iletisim/', views.contact, name='contact'),
    path('ara/', views.search, name='search'),
    path('cerez-politikasi/', views.cookie_policy, name='cookie_policy'),
    path("robots.txt", views.robots_txt),
    
    # Dil değiştirme
    path('dil/<str:language>/', views.set_language, name='set_language'),
    
    # Makale detay
    path('makale/<slug:slug>/', views.article_detail, name='article_detail'),
    
    # AJAX endpoints
    path('ajax/bulten-abone/', views.newsletter_subscribe, name='newsletter_subscribe'),
    path('ajax/iletisim-gonder/', views.contact_submit, name='contact_submit'),
]


