from django.test import TestCase
from django.contrib.auth.models import User
from .models import Auditoria

class AuditoriaModelTest(TestCase):
    def test_crear_registro(self):
        user = User.objects.create(username='testuser')
        registro = Auditoria.objects.create(
            usuario=user,
            accion='registro',
            modulo='usuarios',
            detalles='El usuario se registró correctamente.'
        )
        self.assertEqual(str(registro), f"{registro.fecha} - {user} - registro - usuarios")
