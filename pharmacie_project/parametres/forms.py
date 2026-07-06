from django import forms
from django.core.files.uploadedfile import UploadedFile
from .models import Parametres

class ParametresForm(forms.ModelForm):
    class Meta:
        model = Parametres
        fields = '__all__'
        widgets = {
            'nom_pharmacie': forms.TextInput(attrs={'class': 'form-control'}),
            'slogan': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'couleur': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'langue': forms.Select(attrs={'class': 'form-control'}),
            'devise': forms.TextInput(attrs={'class': 'form-control'}),
            'format_date': forms.TextInput(attrs={'class': 'form-control'}),
            'session_duree': forms.NumberInput(attrs={'class': 'form-control', 'min': 5}),
            'tentatives_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')
        if isinstance(logo, UploadedFile):
            # Limite à 2MB
            if logo.size > 2 * 1024 * 1024:
                raise forms.ValidationError("Le logo ne doit pas dépasser 2MB.")
            # Vérification du type MIME
            if not logo.content_type in ['image/jpeg', 'image/png']:
                raise forms.ValidationError("Le format doit être JPG ou PNG.")
        return logo
