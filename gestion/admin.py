from django.contrib import admin
from .models import GestionEstacion, RegistroSemanal, EstacionMapping

@admin.register(GestionEstacion)
class GestionEstacionAdmin(admin.ModelAdmin):
    list_display = ('estacion_id', 'estacion', 'mes', 'anio', 'disponible', 'nivel_combustible', 'porcentaje_percent')
    search_fields = ('estacion__nombre', 'estacion__estacion_id')
    list_filter = ('mes', 'anio', 'estacion')
    readonly_fields = ('historico_alarmas',)  # Mostrar histórico solo lectura
    # Puedes agregar los campos w23 y promedio_diario_w23 a list_display si lo deseas

    def estacion_id(self, obj):
        return obj.estacion.estacion_id if obj.estacion else None
    estacion_id.short_description = "ID Estación"

    def porcentaje_percent(self, obj):
        if obj.estacion and obj.estacion.total:
            try:
                return f"{round((obj.nivel_combustible or 0) * 100 / obj.estacion.total, 1)} %"
            except Exception:
                return "0 %"
        return "0 %"
    porcentaje_percent.short_description = "%"

@admin.register(RegistroSemanal)
class RegistroSemanalAdmin(admin.ModelAdmin):
    list_display = ('id', 'gestion', 'fecha_inicio', 'fecha_fin', 'consumo', 'suministro', 'promedio_diario')
    search_fields = ('gestion__estacion__nombre',)
    list_filter = ('fecha_inicio', 'fecha_fin')

@admin.register(EstacionMapping)
class EstacionMappingAdmin(admin.ModelAdmin):
    list_display = ('nombre_externo', 'id_externo', 'estacion')
    search_fields = ('nombre_externo', 'id_externo', 'estacion__nombre')
    list_filter = ('estacion',)
