from django.urls import path
from .views import (
    ListaEstacionesView, GestionEstacionCreateView, GestionEstacionUpdateView,
    GestionEstacionDeleteView, eliminar_gestiones, eliminar_gestion, DetalleGestionEstacionView
)
from .views_import import importar_gestiones  # Asegúrate de tener la vista creada
from . import views

urlpatterns = [
    path('', views.lista_estaciones, name='lista_estaciones'),
    path('registrar/', GestionEstacionCreateView.as_view(), name='registrar_estacion'),
    path('editar/<int:pk>/', GestionEstacionUpdateView.as_view(), name='editar_gestion_estacion'),
    path('gestion-estacion/<int:pk>/eliminar/', GestionEstacionDeleteView.as_view(), name='eliminar_gestion_estacion'),
    path('importar/', importar_gestiones, name='importar_gestiones'),
    path('eliminar-multiples/', eliminar_gestiones, name='eliminar_gestiones'),
    path('eliminar/<int:id>/', eliminar_gestion, name='eliminar_gestion'),  # <--- nueva ruta para fetch JS
    path('detalle/<int:pk>/', DetalleGestionEstacionView.as_view(), name='detalle_gestion_estacion'),
    path('estacion/<int:estacion_id>/actualizar_consumo/', views.actualizar_consumo_estacion, name='actualizar_consumo_estacion'),
]
