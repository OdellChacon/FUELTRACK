from django import forms
from .models import Estacion

class EstacionForm(forms.ModelForm):
    class Meta:
        model = Estacion
        fields = '__all__'
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }
