from django import forms
from .models import Medicament, Categorie, Etagere

class MedicamentForm(forms.ModelForm):
    class Meta:
        model = Medicament
        fields = [
            'image', 'nom', 'categorie', 'etagere', 'code_barre', 'description',
            'prix_achat', 'prix_vente', 'date_expiration',
            'quantite_stock', 'seuil_alerte'
        ]
        widgets = {
            'date_expiration': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'description': forms.Textarea(attrs={'rows': 3}),
        }


class EtagereForm(forms.ModelForm):
    class Meta:
        model = Etagere
        fields = ['code', 'nom', 'couleur', 'icone', 'emplacement']
        widgets = {
            'couleur': forms.TextInput(attrs={'type': 'color', 'style': 'width:60px; height:42px; padding:4px; cursor:pointer;'}),
        }