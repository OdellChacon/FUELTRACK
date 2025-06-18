from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Contraseña'
        }),
        required=False
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500',
            'placeholder': 'Confirmar contraseña'
        }),
        required=False
    )

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

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")
        if self.instance.pk is None:  # Solo al crear
            if not password1 or not password2:
                self.add_error('password1', "Debe ingresar una contraseña.")
            elif password1 != password2:
                self.add_error('password2', "Las contraseñas no coinciden.")
        return cleaned_data
