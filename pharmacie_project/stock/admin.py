from django.contrib import admin
from .models import MouvementStock

@admin.register(MouvementStock)
class MouvementStockAdmin(admin.ModelAdmin):
    list_display = ['medicament', 'type_mouvement', 'quantite', 'utilisateur', 'date']
    list_filter = ['type_mouvement']