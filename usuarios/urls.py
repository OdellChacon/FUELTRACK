from django.urls import path
from . import views

urlpatterns = [
    path('listar/', views.listar_usuarios, name='listar_usuarios'),
    path('registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('editar/<int:usuario_id>/', views.editar_usuario, name='editar_usuario'),
    path('eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),
    path('eliminar/', views.eliminar_usuarios, name='eliminar_usuarios'),
    path('importar/', views.importar_usuarios, name='importar_usuarios'),
    path('exportar/<str:formato>/', views.exportar_usuarios, name='exportar_usuarios'),
]
