from django.db import models
from django.conf import settings

class Auditoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    accion = models.CharField(max_length=100)
    modulo = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)
    detalles = models.TextField(blank=True)
    ip = models.GenericIPAddressField(null=True, blank=True)  # Nuevo campo para IP

    def usuario_display(self):
        if self.usuario:
            # Si el modelo usuario tiene 'nombre', úsalo, si no, usa username/email
            return getattr(self.usuario, 'nombre', None) or getattr(self.usuario, 'username', None) or getattr(self.usuario, 'email', None)
        return "anónimo"

    def __str__(self):
        return f"{self.fecha} - {self.usuario_display()} - {self.accion} - {self.modulo} - {self.ip}"
