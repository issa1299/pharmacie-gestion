from django import forms
from .models import Client
from common.forms import StyledModelForm


class ClientForm(StyledModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'telephone', 'email', 'adresse', 'date_naissance']
        widgets = {
            'nom': forms.TextInput(attrs={
                'placeholder': 'Ex : Diallo', 'autofocus': True}),
            'prenom': forms.TextInput(attrs={
                'placeholder': 'Ex : Fatoumata'}),
            'telephone': forms.TextInput(attrs={
                'placeholder': 'Ex : +223 76 00 00 00'}),
            'email': forms.EmailInput(attrs={
                'placeholder': 'exemple@mail.com'}),
            'date_naissance': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'
            ),
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }