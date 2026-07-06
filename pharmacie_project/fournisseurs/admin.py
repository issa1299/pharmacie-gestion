from django.contrib import admin
from .models import Fournisseur

@admin.register(Fournisseur)
class FournisseurAdmin(admin.ModelAdmin):
    list_display = ['nom', 'telephone', 'email', 'created_at']
    search_fields = ['nom', 'telephone']