from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.listar_estaciones, name='listar_estaciones'),
    path('registrar/', views.registrar_estacion, name='registrar_estacion'),
    path('editar/<int:estacion_id>/', views.editar_estacion, name='editar_estacion'),
    path('eliminar/<int:estacion_id>/', views.eliminar_estacion, name='eliminar_estacion'),
    path('eliminar/', views.eliminar_estaciones, name='eliminar_estaciones'),  # Nueva ruta para eliminación masiva
    path('importar/<str:formato>/', views.importar_estaciones, name='importar_estaciones'),
    path('exportar/<str:formato>/', views.exportar_estaciones, name='exportar_estaciones'),
    path('eliminar/<int:estacion_id>/', views.eliminar_estacion_individual, name='eliminar_estacion_individual'),
]
