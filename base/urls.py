from django.urls import path
from . import views
from .views import dashboard

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', dashboard, name='dashboard'),  # Vista de ejemplo para redirección
]
