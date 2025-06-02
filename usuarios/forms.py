from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['email', 'nombre', 'is_active', 'is_staff']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Correo electrónico'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
                'placeholder': 'Nombre completo'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'hidden'
            }),
            'is_staff': forms.CheckboxInput(attrs={
                'class': 'hidden'
            }),
        }
        labels = {
            'email': 'Correo Electrónico',
            'nombre': 'Nombre Completo',
            'is_active': '¿Activo?',
            'is_staff': '¿Es Staff?',
        }
