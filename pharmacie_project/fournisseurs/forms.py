from django import forms
from .models import Fournisseur

_STYLE_TEXT = {'class': 'form-control'}


class _StyledModelForm(forms.ModelForm):
    """Ajoute automatiquement form-control à chaque champ."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            for k, v in _STYLE_TEXT.items():
                field.widget.attrs.setdefault(k, v)


class FournisseurForm(_StyledModelForm):
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