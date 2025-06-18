from django.db import models
from estaciones.models import Estacion
from datetime import datetime, timedelta
import math
from calendar import monthrange

class RegistroSemanal(models.Model):
    gestion = models.ForeignKey('GestionEstacion', on_delete=models.CASCADE, related_name="registros_semanales")
    semana = models.PositiveIntegerField()  
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    consumo = models.FloatField(null=True, blank=True)
    suministro = models.FloatField(null=True, blank=True)
    promedio_diario = models.FloatField(null=True, blank=True)

    class Meta:
        verbose_name = "Registro Semanal"
        verbose_name_plural = "Registros Semanales"
        unique_together = ("gestion", "semana")

    def __str__(self):
        return f"Semana {self.semana} - {self.gestion.estacion.nombre}"

    @staticmethod
    def generar_semanas(gestion, fecha_inicio=None):
        """
        Genera automáticamente registros semanales a partir de una fecha.
        """
        if not fecha_inicio:
            fecha_inicio = datetime.now().date()
        semana_actual = fecha_inicio.isocalendar()[1]
        for i in range(4):  
            fecha_inicio_semana = fecha_inicio + timedelta(weeks=i)
            fecha_fin_semana = fecha_inicio_semana + timedelta(days=6)
            RegistroSemanal.objects.get_or_create(
                gestion=gestion,
                semana=semana_actual + i,
                defaults={
                    "fecha_inicio": fecha_inicio_semana,
                    "fecha_fin": fecha_fin_semana,
                },
            )

class GestionEstacion(models.Model):
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE, related_name='gestiones')
    semana = models.CharField(max_length=10)  # Ej: 'W19', 'W20', etc. o 'MAYO'

    # NUEVO: Campos para mes y año
    mes = models.PositiveSmallIntegerField("Mes", null=True, blank=True)  # 1=Enero, 12=Diciembre
    anio = models.PositiveSmallIntegerField("Año", null=True, blank=True)

    # Campos traídos de Estacion (solo lectura, no editables aquí)
    # ID, REGIÓN, MERCADO, NOMBRE, CONSUMO, TANQUE BASE, TANQUE EXTERNO, TOTAL, CAPACIDAD ANTERIOR
    # Se acceden como: self.estacion.<campo>

    # Editable por teclado
    disponible = models.FloatField("DISPONIBLE (LTS)", null=True, blank=True)

    # Campos semanales (editables)
    suministro_w19 = models.FloatField(null=True, blank=True, default=0)
    horas_trabajo_w19 = models.FloatField(null=True, blank=True, default=0)
    suministro_w20 = models.FloatField(null=True, blank=True, default=0)
    horas_trabajo_w20 = models.FloatField(null=True, blank=True, default=0)
    suministro_w21 = models.FloatField(null=True, blank=True, default=0)
    horas_trabajo_w21 = models.FloatField(null=True, blank=True, default=0)
    suministro_w22 = models.FloatField(null=True, blank=True, default=0)
    horas_trabajo_w22 = models.FloatField(null=True, blank=True, default=0)
    suministro_w23 = models.FloatField(null=True, blank=True, default=0)
    horas_trabajo_w23 = models.FloatField(null=True, blank=True, default=0)

    # Promedio diario (calculado)
    promedio_diario_w19 = models.FloatField(null=True, blank=True, editable=False)
    promedio_diario_w20 = models.FloatField(null=True, blank=True, editable=False)
    promedio_diario_w21 = models.FloatField(null=True, blank=True, editable=False)
    promedio_diario_w22 = models.FloatField(null=True, blank=True, editable=False)
    promedio_diario_w23 = models.FloatField(null=True, blank=True, editable=False)

    # Calculados
    hrs_total = models.FloatField(null=True, blank=True, editable=False)
    hrs_promedio_mensual = models.FloatField(null=True, blank=True, editable=False)
    nivel_combustible = models.FloatField(null=True, blank=True, editable=False)  # = NIVEL
    porcentaje = models.FloatField(null=True, blank=True, editable=False)         # = %
    autonomia_hrs = models.FloatField(null=True, blank=True, editable=False)
    necesario_100 = models.FloatField(null=True, blank=True, editable=False)

    # Horas vacio/real
    vacio_24 = models.FloatField(null=True, blank=True, editable=False)
    real_24 = models.FloatField(null=True, blank=True, editable=False)
    vacio_36 = models.FloatField(null=True, blank=True, editable=False)
    real_36 = models.FloatField(null=True, blank=True, editable=False)
    vacio_48 = models.FloatField(null=True, blank=True, editable=False)
    real_48 = models.FloatField(null=True, blank=True, editable=False)
    vacio_72 = models.FloatField(null=True, blank=True, editable=False)
    real_72 = models.FloatField(null=True, blank=True, editable=False)
    vacio_96 = models.FloatField(null=True, blank=True, editable=False)
    real_96 = models.FloatField(null=True, blank=True, editable=False)

    observaciones = models.TextField(null=True, blank=True)
    historico_alarmas = models.TextField(null=True, blank=True)  # <-- Agrega este campo
    fecha_registro = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Gestión de estación"
        verbose_name_plural = "Gestiones de estaciones"

    # Métodos de cálculo según fórmulas de Excel
    def calcular_promedio_diario(self, horas_trabajo):
        return (horas_trabajo or 0) / 7

    def calcular_hrs_total(self):
        return sum([
            self.horas_trabajo_w19 or 0,
            self.horas_trabajo_w20 or 0,
            self.horas_trabajo_w21 or 0,
            self.horas_trabajo_w22 or 0,
            self.horas_trabajo_w23 or 0  # NUEVO
        ])

    def calcular_hrs_promedio_mensual(self, hrs_total):
        # Usa el número real de días del mes
        if self.mes and self.anio:
            dias_mes = monthrange(self.anio, self.mes)[1]
        else:
            dias_mes = 31
        return (hrs_total or 0) / dias_mes

    def calcular_nivel_combustible(self):
        capacidad_anterior = self.estacion.capacidad_anterior if self.estacion else 0
        consumo = self.estacion.consumo if self.estacion else 0
        suma_suministros = (
            (self.suministro_w19 or 0) +
            (self.suministro_w20 or 0) +
            (self.suministro_w21 or 0) +
            (self.suministro_w22 or 0) +
            (self.suministro_w23 or 0)  # NUEVO
        )
        hrs_total = self.hrs_total or 0
        print("DEBUG NIVEL DE COMBUSTIBLE:",
              "capacidad_anterior=", capacidad_anterior,
              "suministro_w19=", self.suministro_w19,
              "suministro_w20=", self.suministro_w20,
              "suministro_w21=", self.suministro_w21,
              "suministro_w22=", self.suministro_w22,
              "hrs_total=", hrs_total,
              "consumo=", consumo)
        nivel_comb = capacidad_anterior + suma_suministros - (hrs_total * consumo)
        return max(nivel_comb, 0)

    def calcular_porcentaje(self, nivel_combustible):
        total = self.estacion.total if self.estacion else 0
        try:
            return nivel_combustible / total if total else 0
        except Exception:
            return 0

    def calcular_autonomia(self, nivel_combustible):
        consumo = self.estacion.consumo if self.estacion else 0
        if consumo:
            return nivel_combustible / consumo
        return 0

    def calcular_necesario_100(self, nivel_combustible):
        total = self.estacion.total if self.estacion else 0
        return total - nivel_combustible

    def calcular_vacio(self, horas):
        consumo = self.estacion.consumo if self.estacion else 0
        return consumo * horas

    def calcular_real(self, horas, autonomia_hrs, nivel_combustible):
        consumo = self.estacion.consumo if self.estacion else 0
        if autonomia_hrs > horas:
            return 0
        return (horas * consumo) - nivel_combustible

    def safe_int(self, value):
        try:
            if value is None or (isinstance(value, float) and math.isnan(value)):
                return 0
            return int(round(value))
        except Exception:
            return 0

    def save(self, *args, **kwargs):
        # Promedios diarios
        self.promedio_diario_w19 = self.calcular_promedio_diario(self.horas_trabajo_w19)
        self.promedio_diario_w20 = self.calcular_promedio_diario(self.horas_trabajo_w20)
        self.promedio_diario_w21 = self.calcular_promedio_diario(self.horas_trabajo_w21)
        self.promedio_diario_w22 = self.calcular_promedio_diario(self.horas_trabajo_w22)
        self.promedio_diario_w23 = self.calcular_promedio_diario(self.horas_trabajo_w23)

        # HRS TOTAL y PROMEDIO MENSUAL (usar variables locales)
        hrs_total = self.calcular_hrs_total()
        self.hrs_total = hrs_total
        self.hrs_promedio_mensual = self.calcular_hrs_promedio_mensual(hrs_total)

        # NIVEL DE COMBUSTIBLE (usar hrs_total recién calculado)
        capacidad_anterior = self.estacion.capacidad_anterior if self.estacion else 0
        consumo = self.estacion.consumo if self.estacion else 0
        suma_suministros = (
            (self.suministro_w19 or 0) +
            (self.suministro_w20 or 0) +
            (self.suministro_w21 or 0) +
            (self.suministro_w22 or 0) +
            (self.suministro_w23 or 0)  # NUEVO
        )
        nivel_comb = capacidad_anterior + suma_suministros - (hrs_total * consumo)
        nivel_comb_redondeado = self.safe_int(max(nivel_comb, 0))
        self.nivel_combustible = nivel_comb_redondeado

        # PORCENTAJE y %
        self.porcentaje = self.calcular_porcentaje(self.nivel_combustible)
        self.autonomia_hrs = self.safe_int(self.calcular_autonomia(self.nivel_combustible))
        self.necesario_100 = self.calcular_necesario_100(self.nivel_combustible)
        self.vacio_24 = self.calcular_vacio(24)
        self.real_24 = self.calcular_real(24, self.autonomia_hrs, self.nivel_combustible)
        self.vacio_36 = self.calcular_vacio(36)
        self.real_36 = self.calcular_real(36, self.autonomia_hrs, self.nivel_combustible)
        self.vacio_48 = self.calcular_vacio(48)
        self.real_48 = self.calcular_real(48, self.autonomia_hrs, self.nivel_combustible)
        self.vacio_72 = self.calcular_vacio(72)
        self.real_72 = self.calcular_real(72, self.autonomia_hrs, self.nivel_combustible)
        self.vacio_96 = self.calcular_vacio(96)
        self.real_96 = self.calcular_real(96, self.autonomia_hrs, self.nivel_combustible)

        super().save(*args, **kwargs)

    @property
    def porcentaje_100(self):
        """
        Devuelve el porcentaje de combustible en formato 0-100.
        """
        if self.estacion and self.estacion.total:
            try:
                return round((self.nivel_combustible or 0) * 100 / self.estacion.total, 1)
            except Exception:
                return 0
        return 0

class EventoImportado(models.Model):
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    descripcion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('estacion', 'fecha_inicio', 'fecha_fin')
        verbose_name = "Evento Importado"
        verbose_name_plural = "Eventos Importados"

    def __str__(self):
        return f"{self.estacion} | {self.fecha_inicio} - {self.fecha_fin}"

class EstacionMapping(models.Model):
    nombre_externo = models.CharField(max_length=100)
    id_externo = models.CharField(max_length=50, blank=True, null=True)
    estacion = models.ForeignKey(Estacion, on_delete=models.CASCADE)
    # Puedes agregar campos para normalización o alias si lo deseas

    def __str__(self):
        return f"{self.nombre_externo} ({self.id_externo}) -> {self.estacion.nombre}"

class ComentarioGestion(models.Model):
    gestion = models.ForeignKey(GestionEstacion, on_delete=models.CASCADE, related_name='comentarios')
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    autor = models.CharField(max_length=100, blank=True, null=True)  # Opcional: para identificar al usuario

    def __str__(self):
        return f"Comentario en {self.gestion} - {self.fecha:%Y-%m-%d %H:%M}"

class Estacion(models.Model):
    # ...existing code...
    # Añade estos campos al modelo Estacion
    tanque_reserva_condenado = models.BooleanField(default=False)
    tanque_base_condenado = models.BooleanField(default=False)
    tanque_externo_condenado = models.BooleanField(default=False)
    # ...existing code...
