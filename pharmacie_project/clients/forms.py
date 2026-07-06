from django import forms
from .models import Client

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'telephone', 'email', 'adresse', 'date_naissance']
        widgets = {
            'date_naissance': forms.DateInput(
                attrs={'type': 'date'}, format='%Y-%m-%d'
            ),
            'adresse': forms.Textarea(attrs={'rows': 2}),
        }