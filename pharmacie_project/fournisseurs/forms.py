from django import forms
from .models import Fournisseur
from common.forms import StyledModelForm


class FournisseurForm(StyledModelForm):
    class Meta:
        model = Fournisseur
        fields = ['nom', 'telephone', 'email', 'adresse']
        widgets = {
            'nom': forms.TextInput(attrs={
                'placeholder': 'Ex : Labo Diallo & Fils', 'autofocus': True}),
            'telephone': forms.TextInput(attrs={
                'placeholder': 'Ex : +223 76 00 00 00'}),
            'email': forms.EmailInput(attrs={
                'placeholder': 'contact@fournisseur.com'}),
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }