from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Usuario

class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'is_active', 'is_staff')

class UsuarioChangeForm(UserChangeForm):
    class Meta:
        model = Usuario
        fields = ('email', 'nombre', 'is_active', 'is_staff')

class UsuarioAdmin(BaseUserAdmin):
    add_form = UsuarioCreationForm
    form = UsuarioChangeForm
    model = Usuario
    list_display = ('email', 'nombre', 'is_active', 'is_staff')
    list_filter = ('is_active', 'is_staff')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('nombre',)}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nombre', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}
        ),
    )
    search_fields = ('email', 'nombre')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)

admin.site.register(Usuario, UsuarioAdmin)
