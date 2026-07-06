from django.contrib import admin
from .models import Parametres

@admin.register(Parametres)
class ParametresAdmin(admin.ModelAdmin):
    list_display = ['nom_pharmacie', 'telephone', 'email']
    fieldsets = (
        ('Informations de la pharmacie', {
            'fields': ('nom_pharmacie', 'slogan', 'adresse', 'telephone', 'email', 'logo')
        }),
        ('Apparence', {
            'fields': ('couleur', 'langue', 'devise', 'format_date')
        }),
        ('Sécurité', {
            'fields': ('session_duree', 'tentatives_max')
        }),
    )