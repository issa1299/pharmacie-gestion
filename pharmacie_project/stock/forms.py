from django import forms
from .models import MouvementStock

class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['medicament', 'type_mouvement', 'quantite', 'motif']
        widgets = {
            'medicament': forms.Select(attrs={'class': 'form-select'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1,
                'placeholder': 'Ex : 50',
            }),
            'motif': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : Livraison fournisseur, Vente...'
            }),
        }

    def clean_quantite(self):
        quantite = self.cleaned_data['quantite']
        if quantite <= 0:
            raise forms.ValidationError("La quantité doit être supérieure à zéro.")
        return quantite