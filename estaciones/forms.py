from django import forms
from .models import Estacion

class EstacionForm(forms.ModelForm):
    class Meta:
        model = Estacion
        # Excluye el campo 'id' (clave primaria automática)
        exclude = ('id',)
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }
