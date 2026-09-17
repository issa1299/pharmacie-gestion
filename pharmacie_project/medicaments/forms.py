from django import forms
from .models import Medicament, Categorie, Etagere
from common.forms import StyledModelForm


class MedicamentForm(StyledModelForm):
    class Meta:
        model = Medicament
        fields = [
            'image', 'nom', 'categorie', 'etagere', 'code_barre', 'description',
            'prix_achat', 'prix_vente', 'date_expiration',
            'quantite_stock', 'seuil_alerte'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={
                'placeholder': 'Ex : Paracétamol 500 mg', 'autofocus': True}),
            'code_barre': forms.TextInput(attrs={
                'placeholder': 'Scanner ou saisir le code-barres…'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'date_expiration': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'),
            'prix_achat': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'prix_vente': forms.NumberInput(attrs={'min': 0, 'step': '0.01'}),
            'quantite_stock': forms.NumberInput(attrs={'min': 0}),
            'seuil_alerte': forms.NumberInput(attrs={'min': 0}),
        }

    def clean(self):
        cleaned = super().clean()
        achat = cleaned.get('prix_achat')
        vente = cleaned.get('prix_vente')
        if achat is not None and vente is not None and vente < achat:
            self.add_error(
                'prix_vente',
                "Le prix de vente est inférieur au prix d'achat — vérifiez la marge."
            )
        return cleaned


class EtagereForm(forms.ModelForm):
    class Meta:
        model = Etagere
        fields = ['code', 'nom', 'couleur', 'icone', 'emplacement']
        widgets = {
            'couleur': forms.TextInput(attrs={'type': 'color', 'style': 'width:60px; height:42px; padding:4px; cursor:pointer;'}),
        }