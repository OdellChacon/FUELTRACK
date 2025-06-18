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
    path('importar_horas_trabajo/', views.importar_horas_trabajo, name='importar_horas_trabajo'),
    path('importar_horas_trabajo_detalle/', views.importar_horas_trabajo_detalle, name='importar_horas_trabajo_detalle'),
    path('importar_horas_trabajo_pegar/', views.importar_horas_trabajo_pegar, name='importar_horas_trabajo_pegar'),
    path('importar_horas_masivo/', views.importar_horas_masivo, name='importar_horas_masivo'),
    path('confirmar_importar_horas_masivo/', views.confirmar_importar_horas_masivo, name='confirmar_importar_horas_masivo'),
    path('gestion/<int:gestion_id>/actualizar_semana/', views.actualizar_semana_gestion, name='actualizar_semana_gestion'),
    path('historico_alertas/', views.historico_alertas, name='historico_alertas'),
    path('actualizar_observaciones/<int:gestion_id>/', views.actualizar_observaciones_gestion, name='actualizar_observaciones_gestion'),
    path('comentarios_gestion/<int:gestion_id>/', views.comentarios_gestion, name='comentarios_gestion'),
    path('comentarios/<int:gestion_id>/', views.comentarios_gestion, name='comentarios_gestion'),
    path('estacion/<int:estacion_id>/actualizar_capacidad/', views.actualizar_capacidad_anterior, name='actualizar_capacidad_anterior'),
    path('gestion/<int:gestion_id>/actualizar_disponible/', views.actualizar_disponible_gestion, name='actualizar_disponible_gestion'),
    path('gestion/<int:gestion_id>/actualizar_nivel/', views.actualizar_nivel_gestion, name='actualizar_nivel_gestion'),
    path('estacion/<int:estacion_id>/actualizar_tanque_base/', views.actualizar_tanque_base, name='actualizar_tanque_base'),
    path('estacion/<int:estacion_id>/actualizar_tanque_externo/', views.actualizar_tanque_externo, name='actualizar_tanque_externo'),
    path('estacion/<int:estacion_id>/toggle_tanque_reserva/', views.toggle_tanque_reserva, name='toggle_tanque_reserva'),
    path('estacion/<int:estacion_id>/toggle_tanque_base/', views.toggle_tanque_base, name='toggle_tanque_base'),
    path('estacion/<int:estacion_id>/toggle_tanque_externo/', views.toggle_tanque_externo, name='toggle_tanque_externo'),
]
