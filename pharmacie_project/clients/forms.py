from django import forms
from .models import Client

_STYLE_TEXT = {'class': 'form-control'}
_STYLE_SELECT = {'class': 'form-select'}


class _StyledModelForm(forms.ModelForm):
    """Ajoute automatiquement form-control / form-select à chaque champ."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            css = _STYLE_SELECT if isinstance(
                widget, (forms.Select, forms.SelectMultiple)
            ) else _STYLE_TEXT
            widget.attrs.update({k: v for k, v in css.items() if k not in widget.attrs})


class ClientForm(_StyledModelForm):
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