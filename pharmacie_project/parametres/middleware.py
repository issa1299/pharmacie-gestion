from .models import Parametres
from django.utils import translation


class SessionDurationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            params, _ = Parametres.objects.get_or_create(pk=1)
            request.session.set_expiry(params.session_duree * 60)

        return self.get_response(request)


class LanguageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        params, _ = Parametres.objects.get_or_create(pk=1)
        langue = params.langue if params.langue in ['fr', 'en', 'ar'] else 'fr'
        
        translation.activate(langue)
        request.LANGUAGE_CODE = langue
        request.session['django_language'] = langue
        
        return self.get_response(request)
