from django.contrib import admin
from .models import Estacion

@admin.register(Estacion)
class EstacionAdmin(admin.ModelAdmin):
    list_display = ('id', 'mercado', 'nombre', 'estado', 'tipo_estacion', 'mes', 'anio')
    search_fields = ('id', 'mercado', 'nombre', 'estado', 'tipo_estacion')
    list_filter = ('mes', 'anio')
