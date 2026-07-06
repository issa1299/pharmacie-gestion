from django import forms
from .models import MouvementStock

class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['medicament', 'type_mouvement', 'quantite', 'motif']
        widgets = {
            'motif': forms.TextInput(attrs={
                'placeholder': 'Ex: Livraison fournisseur, Vente...'
            }),
        }

    def clean_quantite(self):
        quantite = self.cleaned_data['quantite']
        if quantite <= 0:
            raise forms.ValidationError("La quantité doit être supérieure à zéro.")
        return quantite