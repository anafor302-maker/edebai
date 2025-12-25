from .models import CookieConsent


def language_context(request):
    """Her template'de kullanılabilecek dil bilgisi"""
    # Cookie'den dil tercihini al
    language = request.COOKIES.get('language', 'tr')
    
    # Session'dan da kontrol et
    if hasattr(request, 'session'):
        language = request.session.get('language', language)
    
    return {
        'LANGUAGE_CODE': language,
    }


def cookie_consent_context(request):
    """Çerez onayı banner için"""
    cookie_consent = CookieConsent.objects.filter(is_active=True).first()
    return {
        'cookie_consent': cookie_consent,
    }