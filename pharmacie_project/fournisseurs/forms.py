from django import forms
from .models import Fournisseur

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'telephone', 'email', 'adresse']
        widgets = {
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }