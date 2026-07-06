from django.contrib import admin
from .models import Vente, LigneVente

class LigneVenteInline(admin.TabularInline):
    model = LigneVente
    extra = 0

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ['numero_facture', 'client', 'total', 'statut', 'date_vente']
    inlines = [LigneVenteInline]