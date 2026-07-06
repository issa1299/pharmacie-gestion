from django.urls import path
from . import views

app_name = 'parametres'

urlpatterns = [
    path('', views.parametres, name='index'),
    path('api/language/', views.LanguageAPIView.as_view(), name='language_api'),
    # Alias pour compatibilité
    path('api/change-language/', views.LanguageAPIView.as_view(), name='change_language'),
    # Page de test de l'API
    path('api/test/', views.api_test, name='api_test'),
]