from django.shortcuts import render
from .models import Auditoria
from django.contrib.auth.decorators import login_required

@login_required
def lista_auditoria(request):
    registros = Auditoria.objects.all().order_by('-fecha')
    return render(request, 'auditoria/lista.html', {'registros': registros})

def registrar_evento_auditoria(request, accion, modulo, detalles=""):
    usuario = request.user if hasattr(request, "user") and request.user.is_authenticated else None
    ip = None
    if hasattr(request, "META"):
        ip = request.META.get('REMOTE_ADDR')
    Auditoria.objects.create(
        usuario=usuario,
        accion=accion,
        modulo=modulo,
        detalles=detalles,
        ip=ip
    )

# Create your views here.
