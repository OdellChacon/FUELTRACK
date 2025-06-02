from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
import json
from .models import GestionEstacion
from estaciones.models import Estacion
from django import forms
from auditoria.views import registrar_evento_auditoria
from datetime import date

class GestionEstacionForm(forms.ModelForm):
    class Meta:
        model = GestionEstacion
        # Solo excluimos los campos calculados y de solo lectura
        exclude = [
            'promedio_diario_w19', 'promedio_diario_w20', 'promedio_diario_w21', 'promedio_diario_w22',
            'hrs_total', 'hrs_promedio_mensual', 'nivel_combustible', 'porcentaje',
            'autonomia_hrs', 'necesario_100',
            # Si quieres que sean editables, quítalos de aquí
            'vacio_24', 'real_24', 'vacio_36', 'real_36', 'vacio_48', 'real_48',
            'vacio_72', 'real_72', 'vacio_96', 'real_96',
            'fecha_registro', 'semana'  # Eliminar campo semana del formulario
        ]
        labels = {
            "suministro_w19": "Suministro semana 1",
            "horas_trabajo_w19": "Horas de trabajo semana 1",
            "suministro_w20": "Suministro semana 2",
            "horas_trabajo_w20": "Horas de trabajo semana 2",
            "suministro_w21": "Suministro semana 3",
            "horas_trabajo_w21": "Horas de trabajo semana 3",
            "suministro_w22": "Suministro semana 4",
            "horas_trabajo_w22": "Horas de trabajo semana 4",
            # ...otros labels si los necesitas...
        }

    def clean(self):
        cleaned_data = super().clean()
        # Si algún campo semanal está vacío, ponerlo en 0
        for campo in [
            'suministro_w19', 'horas_trabajo_w19',
            'suministro_w20', 'horas_trabajo_w20',
            'suministro_w21', 'horas_trabajo_w21',
            'suministro_w22', 'horas_trabajo_w22'
        ]:
            if cleaned_data.get(campo) is None:
                cleaned_data[campo] = 0
        return cleaned_data

class GestionEstacionUpdateView(UpdateView):
    model = GestionEstacion
    form_class = GestionEstacionForm
    template_name = 'gestion/gestion_estacion_form.html'
    success_url = reverse_lazy('lista_estaciones')

class GestionEstacionCreateView(CreateView):
    model = GestionEstacion
    form_class = GestionEstacionForm
    template_name = 'gestion/gestion_estacion_form.html'
    success_url = reverse_lazy('lista_estaciones')

class ListaEstacionesView(ListView):
    model = GestionEstacion
    template_name = 'gestion/lista_estaciones.html'
    context_object_name = 'gestiones'

    def get_queryset(self):
        qs = super().get_queryset().select_related('estacion').prefetch_related('registros_semanales')
        for gestion in qs:
            semanas = list(gestion.registros_semanales.all().order_by('semana'))
            while len(semanas) < 4:
                semanas.append(None)
            gestion.semanas_tabla = semanas[:4]
        return qs

@method_decorator(csrf_exempt, name='dispatch')
class GestionEstacionDeleteView(View):
    def post(self, request, pk):
        gestion = get_object_or_404(GestionEstacion, pk=pk)
        gestion.delete()
        registrar_evento_auditoria(request, "Eliminar", "Gestiones", f"Gestión eliminada: {pk}")
        return JsonResponse({'success': True, 'message': 'Gestión eliminada correctamente.'})

@csrf_exempt
def eliminar_gestiones(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ids = data.get('ids', [])
            if not ids:
                return JsonResponse({'success': False, 'message': 'No se proporcionaron IDs para eliminar.'}, status=400)
            GestionEstacion.objects.filter(id__in=ids).delete()
            registrar_evento_auditoria(request, "Eliminar", "Gestiones", f"Gestiones eliminadas: {ids}")
            return JsonResponse({'success': True, 'message': 'Registros eliminados correctamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al eliminar registros: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

class DetalleGestionEstacionView(DetailView):
    model = GestionEstacion
    template_name = 'gestion/detalle_gestion_estacion.html'
    context_object_name = 'gestion'

@csrf_exempt
def eliminar_gestion(request, id):
    if request.method == 'POST':
        try:
            gestion = GestionEstacion.objects.get(pk=id)
            gestion.delete()
            registrar_evento_auditoria(request, "Eliminar", "Gestiones", f"Gestión eliminada: {id}")
            return JsonResponse({'success': True, 'message': 'Eliminado correctamente.'})
        except GestionEstacion.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'No encontrado.'})
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@csrf_exempt
@login_required
def actualizar_consumo_estacion(request, estacion_id):
    if request.method == "POST":
        import json
        data = json.loads(request.body)
        try:
            estacion = Estacion.objects.get(id=estacion_id)
            estacion.consumo = float(data.get("consumo", 0))
            estacion.save()
            return JsonResponse({"success": True})
        except Exception:
            return JsonResponse({"success": False})
    return JsonResponse({"success": False})

def lista_estaciones(request):
    mes = int(request.GET.get('mes', date.today().month))
    anio = int(request.GET.get('anio', date.today().year))
    gestiones = GestionEstacion.objects.filter(mes=mes, anio=anio)
    meses = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
    ]
    anios = list(range(2023, 2031))
    context = {
        'gestiones': gestiones,
        'mes': mes,
        'anio': anio,
        'meses': meses,
        'anios': anios,
    }
    return render(request, 'gestion/lista_estaciones.html', context)
