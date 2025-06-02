from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from estaciones.models import Estacion
from usuarios.models import Usuario
from auditoria.models import Auditoria
from django.db.models import Count

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')  # Usar el campo 'email'
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)  # Autenticación con email
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Redirigir al dashboard después de iniciar sesión
        else:
            messages.error(request, 'Credenciales inválidas. Inténtalo de nuevo.')
    return render(request, 'base/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirige al login después de cerrar sesión

@login_required(login_url='login')
def dashboard(request):
    estaciones_count = Estacion.objects.count()
    usuarios_count = Usuario.objects.count()
    # Agrupar por mercado y contar
    estaciones_por_mercado = (
        Estacion.objects.values('mercado')
        .annotate(total=Count('id'))
        .order_by('mercado')
    )
    # Serializar para JS: asegurarse de que sean listas de strings y números
    mercados = [str(item['mercado']) for item in estaciones_por_mercado]
    cantidades = [item['total'] for item in estaciones_por_mercado]
    auditorias_count = Auditoria.objects.count()
    auditoria_reciente = Auditoria.objects.all().order_by('-fecha')[:3]
    return render(request, 'base/dashboard.html', {
        'estaciones_count': estaciones_count,
        'usuarios_count': usuarios_count,
        'mercados': mercados,
        'cantidades': cantidades,
        'auditorias_count': auditorias_count,
        'auditoria_reciente': auditoria_reciente,
    })
