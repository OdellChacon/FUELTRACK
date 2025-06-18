from django.contrib import admin
from .models import Estacion

@admin.register(Estacion)
class EstacionAdmin(admin.ModelAdmin):
    list_display = ('estacion_id', 'nombre', 'estado', 'tipo_estacion', 'mes', 'anio')
    search_fields = ('estacion_id', 'nombre', 'estado', 'tipo_estacion')
    list_filter = ('mes', 'anio')
