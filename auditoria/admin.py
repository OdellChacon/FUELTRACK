from django.contrib import admin
from .models import Auditoria

@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'usuario', 'ip', 'accion', 'modulo')
    search_fields = ('usuario__username', 'usuario__nombre', 'ip', 'accion', 'modulo', 'detalles')
    list_filter = ('modulo', 'accion', 'fecha')
