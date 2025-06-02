from django.urls import path
from .views_import import importar_gestiones

urlpatterns = [
    path('importar/', importar_gestiones, name='importar_gestiones'),
]
