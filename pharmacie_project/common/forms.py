from django import forms

STYLE_TEXT = {'class': 'form-control'}
STYLE_SELECT = {'class': 'form-select'}


class StyledModelForm(forms.ModelForm):
    """Ajoute automatiquement form-control / form-select à chaque champ."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            css = STYLE_SELECT if isinstance(
                widget, (forms.Select, forms.SelectMultiple)
            ) else STYLE_TEXT
            widget.attrs.update({k: v for k, v in css.items() if k not in widget.attrs})
