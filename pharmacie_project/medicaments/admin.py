from django.contrib import admin
from django.utils.html import format_html
from .models import Medicament, Categorie, Etagere


@admin.register(Etagere)
class EtagereAdmin(admin.ModelAdmin):
    list_display = ['code', 'nom', 'couleur', 'emplacement']


@admin.register(Medicament)
class MedicamentAdmin(admin.ModelAdmin):
    list_display = ['apercu_image', 'nom', 'categorie', 'etagere', 'prix_vente', 'quantite_stock']
    list_filter = ['categorie', 'etagere']
    search_fields = ['nom', 'code_barre']
    readonly_fields = ['apercu_image']

    fieldsets = (
        ('Informations générales', {
            'fields': ('nom', 'code_barre', 'description', 'categorie', 'etagere')
        }),
        ('Photo', {
            'fields': ('image', 'apercu_image'),
        }),
        ('Prix & Stock', {
            'fields': ('prix_vente', 'prix_achat', 'quantite_stock', 'seuil_alerte')
        }),
        ('Expiration', {
            'fields': ('date_expiration',)
        }),
    )

    def apercu_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:60px;border-radius:6px;object-fit:contain;" />',
                obj.image.url
            )
        return "—"
    apercu_image.short_description = "Aperçu"


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description']