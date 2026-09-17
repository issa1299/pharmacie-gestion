from django import forms
from .models import MouvementStock


class MouvementStockForm(forms.ModelForm):
    class Meta:
        model = MouvementStock
        fields = ['medicament', 'type_mouvement', 'fournisseur', 'quantite', 'motif']
        widgets = {
            'medicament': forms.Select(attrs={'class': 'form-select'}),
            'type_mouvement': forms.Select(attrs={'class': 'form-select'}),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control', 'min': 1,
                'placeholder': 'Ex : 50',
            }),
            'motif': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex : Livraison fournisseur, Vente...'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from fournisseurs.models import Fournisseur
        self.fields['fournisseur'].queryset = Fournisseur.objects.all()
        self.fields['fournisseur'].required = False
        self.fields['fournisseur'].empty_label = '-- Aucun --'

    def clean_quantite(self):
        quantite = self.cleaned_data['quantite']
        if quantite <= 0:
            raise forms.ValidationError("La quantité doit être supérieure à zéro.")
        return quantite