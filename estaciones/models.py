from django.db import models

class Estacion(models.Model):
    estacion_id = models.IntegerField()  # Identificador de la estación
    region = models.CharField(max_length=100)
    mercado = models.CharField(max_length=100)
    nombre = models.CharField(max_length=255)
    distribuidora = models.CharField(max_length=255)
    tipo_estacion = models.CharField(max_length=100)
    estado = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    modelo = models.CharField(max_length=100)
    serial = models.CharField(max_length=100, blank=True, null=True)  # <--- AGREGADO
    capacidad = models.FloatField()
    consumo = models.FloatField()
    pac = models.CharField(max_length=100)  
    tanque_base = models.FloatField()
    tanque_externo = models.FloatField()
    total = models.FloatField(null=True, blank=True) 
    capacidad_anterior = models.FloatField()
    compens = models.FloatField(null=True, blank=True)  
    nivel_total = models.FloatField(null=True, blank=True)  
    cinco_min = models.FloatField(null=True, blank=True)  
    diez_min = models.FloatField(null=True, blank=True)  
    veinte_min = models.FloatField(null=True, blank=True)  
    fecha = models.DateField()  
    mes = models.PositiveSmallIntegerField("Mes", null=True, blank=True)  # 1=Enero, 12=Diciembre
    anio = models.PositiveSmallIntegerField("Año", null=True, blank=True)
    
    # NUEVO: Estado de condena/bloqueo de tanques
    tanque_reserva_condenado = models.BooleanField(default=False)
    tanque_base_condenado = models.BooleanField(default=False)
    tanque_externo_condenado = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Estación"
        verbose_name_plural = "Estaciones"
        unique_together = ('estacion_id', 'mes', 'anio')  # Un registro por estación/mes/año

    def sincronizar_gestion(self):
        """
        Sincroniza los datos de la estación con todas sus gestiones asociadas.
        """
        for gestion in self.gestiones.all():
            gestion.capacidad_anterior = self.capacidad_anterior
            gestion.nivel = self.nivel_total
            gestion.porcentaje = round((self.nivel_total or 0) / (self.total or 1), 2)
            gestion.save()

    def save(self, *args, **kwargs):
        self.total = (self.tanque_base or 0) + (self.tanque_externo or 0)
        self.nivel_total = (self.capacidad_anterior or 0) + (self.compens or 0)
        self.cinco_min = round((5 / 60) * (self.consumo or 0), 2)
        self.diez_min = round((10 / 60) * (self.consumo or 0), 2)
        self.veinte_min = round((20 / 60) * (self.consumo or 0), 2)
        super().save(*args, **kwargs)
        self.sincronizar_gestion()

    def __str__(self):
        return self.nombre
