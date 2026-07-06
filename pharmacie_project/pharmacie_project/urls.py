from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os
from . import views
from accounts.views import (
    reset_mot_de_passe_demande,
    reset_mot_de_passe_verifier,
    reset_mot_de_passe_nouveau,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Allauth — connexion, inscription, Google, mot de passe oublié
    path('accounts/', include('allauth.urls')),

    # Réinitialisation de mot de passe personnalisée (avec code)
    path('account/reset-password/', reset_mot_de_passe_demande, name='account_reset_password_request'),
    path('account/reset-password/verify/', reset_mot_de_passe_verifier, name='account_verify_code'),
    path('account/reset-password/new/', reset_mot_de_passe_nouveau, name='account_new_password'),

    # Gestion utilisateurs (votre app accounts)
    path('gestion/', include('accounts.urls', namespace='accounts')),

    # Vos apps
    path('medicaments/', include('medicaments.urls', namespace='medicaments')),
    path('stock/', include('stock.urls', namespace='stock')),
    path('ventes/', include('ventes.urls', namespace='ventes')),
    path('clients/', include('clients.urls', namespace='clients')),
    path('fournisseurs/', include('fournisseurs.urls', namespace='fournisseurs')),
    path('rapports/', include('rapports.urls', namespace='rapports')),
    path('parametres/', include('parametres.urls', namespace='parametres')),
    path('', views.dashboard, name='dashboard'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
