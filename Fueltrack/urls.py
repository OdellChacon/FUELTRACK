from django.contrib import admin
from django.urls import path, include
from base import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # <-- Añadido aquí
    path('base/', include('base.urls')),
    path('usuarios/', include('usuarios.urls')),  
    path('estaciones/', include('estaciones.urls')),  
    path('gestion/', include('gestion.urls')),
    path('audit/', include('auditoria.urls')),  # Añade esta línea para el módulo de auditoría
]
