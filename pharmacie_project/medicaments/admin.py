from django.contrib import admin
# pyrefly: ignore [missing-import]
from .models import Medicament, Categorie, Etagere

@admin.register(Etagere)
class EtagereAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'couleur', 'emplacement']

@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie', 'etagere', 'prix_vente', 'quantite_stock']
    list_filter = ['categorie', 'etagere']
    search_fields = ['nom', 'code_barre']

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description']