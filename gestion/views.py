from django.shortcuts import render, get_object_or_404
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic import ListView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
import json
from .models import GestionEstacion, EventoImportado, ComentarioGestion
from estaciones.models import Estacion
from django import forms
from auditoria.views import registrar_evento_auditoria
from datetime import date
from django.views.decorators.http import require_POST
import pandas as pd
import math
from django.views.decorators.csrf import csrf_exempt
from calendar import monthrange
from django.utils import timezone
from django.utils.timezone import make_naive
from .models import EstacionMapping
from .utils import normalizar_nombre

import re
from django.core.paginator import Paginator
import csv
import io

class GestionEstacionForm(forms.ModelForm):
    class Meta:
        model = GestionEstacion
        # Solo excluimos los campos calculados y de solo lectura
        exclude = [
            'promedio_diario_w19', 'promedio_diario_w20', 'promedio_diario_w21', 'promedio_diario_w22', 'promedio_diario_w23',
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
            "suministro_w23": "Suministro semana 5",
            "horas_trabajo_w23": "Horas de trabajo semana 5",
            # ...otros labels si los necesitas...
        }

    def clean(self):
        cleaned_data = super().clean()
        for campo in [
            'suministro_w19', 'horas_trabajo_w19',
            'suministro_w20', 'horas_trabajo_w20',
            'suministro_w21', 'horas_trabajo_w21',
            'suministro_w22', 'horas_trabajo_w22',
            'suministro_w23', 'horas_trabajo_w23'
        ]:
            if cleaned_data.get(campo) is None:
                cleaned_data[campo] = 0
        return cleaned_data

class GestionEstacionUpdateView(UpdateView):
    model = GestionEstacion
    form_class = GestionEstacionForm
    template_name = 'gestion/gestion_estacion_form.html'
    success_url = reverse_lazy('lista_estaciones')

    def form_valid(self, form):
        # Asigna mes y año desde GET o POST, o usa los actuales
        mes = int(self.request.GET.get('mes', self.request.POST.get('mes', date.today().month)))
        anio = int(self.request.GET.get('anio', self.request.POST.get('anio', date.today().year)))
        form.instance.mes = mes
        form.instance.anio = anio
        res = super().form_valid(form)
        registrar_evento_auditoria(self.request, "Editar", "Gestiones", f"Gestión editada: {form.instance.id}")
        return res

class GestionEstacionCreateView(CreateView):
    model = GestionEstacion
    form_class = GestionEstacionForm
    template_name = 'gestion/gestion_estacion_form.html'
    success_url = reverse_lazy('lista_estaciones')

    def form_valid(self, form):
        # Asigna mes y año desde GET o POST, o usa los actuales
        mes = int(self.request.GET.get('mes', self.request.POST.get('mes', date.today().month)))
        anio = int(self.request.GET.get('anio', self.request.POST.get('anio', date.today().year)))
        form.instance.mes = mes
        form.instance.anio = anio
        res = super().form_valid(form)
        registrar_evento_auditoria(self.request, "Crear", "Gestiones", f"Gestión creada: {form.instance.id}")
        return res

class ListaEstacionesView(ListView):
    model = GestionEstacion
    template_name = 'gestion/lista_estaciones.html'
    context_object_name = 'gestiones'

    def get_queryset(self):
        # Filtra por mes y año igual que en estaciones
        mes = int(self.request.GET.get('mes', date.today().month))
        anio = int(self.request.GET.get('anio', date.today().year))
        qs = GestionEstacion.objects.filter(mes=mes, anio=anio).select_related('estacion').prefetch_related('registros_semanales')
        for gestion in qs:
            semanas = list(gestion.registros_semanales.all().order_by('semana'))
            while len(semanas) < 4:
                semanas.append(None)
            gestion.semanas_tabla = semanas[:4]
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mes = int(self.request.GET.get('mes', date.today().month))
        anio = int(self.request.GET.get('anio', date.today().year))
        meses = [
            (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
            (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
            (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre")
        ]
        anios = list(range(2023, 2031))
        context.update({
            'mes': mes,
            'anio': anio,
            'meses': meses,
            'anios': anios,
        })
        return context

@method_decorator(csrf_exempt, name='dispatch')
class GestionEstacionDeleteView(View):
    def post(self, request, pk):
        gestion = get_object_or_404(GestionEstacion, pk=pk)
        # Elimina los eventos importados asociados a la estación, mes y año de la gestión
        EventoImportado.objects.filter(
            estacion=gestion.estacion,
            fecha_inicio__month=gestion.mes,
            fecha_inicio__year=gestion.anio
        ).delete()
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
            gestiones = GestionEstacion.objects.filter(id__in=ids)
            # Elimina los eventos importados asociados a cada gestión
            for gestion in gestiones:
                EventoImportado.objects.filter(
                    estacion=gestion.estacion,
                    fecha_inicio__month=gestion.mes,
                    fecha_inicio__year=gestion.anio
                ).delete()
            gestiones.delete()
            registrar_evento_auditoria(request, "Eliminar", "Gestiones", f"Gestiones eliminadas: {ids}")
            return JsonResponse({'success': True, 'message': 'Registros eliminados correctamente.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error al eliminar registros: {str(e)}'}, status=500)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

class DetalleGestionEstacionView(DetailView):
    model = GestionEstacion
    template_name = 'gestion/detalle_gestion_estacion.html'
    context_object_name = 'gestion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        historico = self.object.historico_alarmas or ""
        # Divide por doble salto de línea para separar bloques de importación
        context['historico_alarmas_bloques'] = [b for b in historico.split('\n\n') if b.strip()]
        return context

@csrf_exempt
def eliminar_gestion(request, id):
    if request.method == 'POST':
        try:
            gestion = GestionEstacion.objects.get(pk=id)
            # Elimina los eventos importados asociados a la estación, mes y año de la gestión
            EventoImportado.objects.filter(
                estacion=gestion.estacion,
                fecha_inicio__month=gestion.mes,
                fecha_inicio__year=gestion.anio
            ).delete()
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
            registrar_evento_auditoria(request, "Editar", "Gestiones", f"Actualizó consumo estación {estacion_id} a {estacion.consumo}")
            return JsonResponse({"success": True})
        except Exception:
            return JsonResponse({"success": False})
    return JsonResponse({"success": False})

@csrf_exempt
@login_required
def actualizar_capacidad_anterior(request, estacion_id):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            estacion = Estacion.objects.get(id=estacion_id)
            estacion.capacidad_anterior = float(data.get("capacidad_anterior", 0))
            estacion.save()
            registrar_evento_auditoria(request, "Editar", "Gestiones", f"Actualizó capacidad_anterior estación {estacion_id} a {estacion.capacidad_anterior}")
            return JsonResponse({"success": True})
        except Exception:
            return JsonResponse({"success": False})
    return JsonResponse({"success": False})

@csrf_exempt
@login_required
def actualizar_disponible_gestion(request, gestion_id):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            gestion = GestionEstacion.objects.get(id=gestion_id)
            gestion.disponible = float(data.get("disponible", 0))
            gestion.save()
            registrar_evento_auditoria(request, "Editar", "Gestiones", f"Actualizó disponible gestión {gestion_id} a {gestion.disponible}")
            return JsonResponse({"success": True})
        except Exception:
            return JsonResponse({"success": False})
    return JsonResponse({"success": False})

@csrf_exempt
@login_required
def actualizar_nivel_gestion(request, gestion_id):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            gestion = GestionEstacion.objects.get(id=gestion_id)
            gestion.nivel_combustible = float(data.get("nivel_combustible", 0))
            gestion.save()
            registrar_evento_auditoria(request, "Editar", "Gestiones", f"Actualizó nivel_combustible gestión {gestion_id} a {gestion.nivel_combustible}")
            return JsonResponse({"success": True})
        except Exception:
            return JsonResponse({"success": False})
    return JsonResponse({"success": False})

@csrf_exempt
@login_required
def actualizar_tanque_base(request, estacion_id):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            estacion = Estacion.objects.get(id=estacion_id)
            estacion.tanque_base = float(data.get("tanque_base", 0))
            estacion.total = (estacion.tanque_base or 0) + (estacion.tanque_externo or 0)
            estacion.save()
            registrar_evento_auditoria(request, "Editar", "Gestiones", f"Actualizó tanque_base estación {estacion_id} a {estacion.tanque_base}")
            return JsonResponse({"success": True, "total": estacion.total})
        except Exception:
            return JsonResponse({"success": False})
    return JsonResponse({"success": False})

@csrf_exempt
@login_required
def actualizar_tanque_externo(request, estacion_id):
    if request.method == "POST":
        data = json.loads(request.body)
        try:
            estacion = Estacion.objects.get(id=estacion_id)
            estacion.tanque_externo = float(data.get("tanque_externo", 0))
            estacion.total = (estacion.tanque_base or 0) + (estacion.tanque_externo or 0)
            estacion.save()
            registrar_evento_auditoria(request, "Editar", "Gestiones", f"Actualizó tanque_externo estación {estacion_id} a {estacion.tanque_externo}")
            return JsonResponse({"success": True, "total": estacion.total})
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

@csrf_exempt
@require_POST
def importar_horas_trabajo(request):
    """
    Importa horas de trabajo desde un archivo Excel de alarmas.
    Asigna automáticamente a la semana correspondiente del mes.
    Evita duplicados por estación, fecha_inicio y fecha_fin.
    """
    file = request.FILES.get('file')
    mes = int(request.POST.get('mes'))
    anio = int(request.POST.get('anio'))
    resumen = []
    nuevos = 0
    duplicados = 0
    duplicados_detalle = []

    if not file:
        return JsonResponse({'success': False, 'message': 'No se envió archivo.'}, status=400)

    try:
        df = pd.read_excel(file)
        cols = [c.lower().strip() for c in df.columns]
        # Reconocer encabezados Occurrence Time y Clear Time
        if set(['occurrence time', 'clear time']).issubset(set(cols)):
            idx_estacion = None  # No hay estación, se debe asignar manualmente o por contexto
            idx_evento = None
            idx_inicio = cols.index('occurrence time')
            idx_fin = cols.index('clear time')
        elif len(cols) >= 4 and 'motogenerador' in cols[1]:
            idx_estacion, idx_evento, idx_inicio, idx_fin = 0, 1, 2, 3
        elif len(cols) >= 5 and 'motogenerador' in cols[1]:
            idx_estacion, idx_evento, idx_inicio, idx_fin = 0, 1, 3, 4
        else:
            return JsonResponse({'success': False, 'message': 'Formato de archivo no reconocido.'}, status=400)

        for _, row in df.iterrows():
            if idx_estacion is not None:
                estacion_nombre = str(row[idx_estacion]).strip()
            else:
                estacion_nombre = None  # O asignar por contexto si aplica
            if idx_evento is not None:
                evento = str(row[idx_evento])
            else:
                evento = "Motogenerador (importado Occurrence Time)"
            fecha_inicio = pd.to_datetime(row[idx_inicio])
            # IGNORAR registros sin fecha de fin válida
            valor_fecha_fin = row[idx_fin]
            if pd.isna(valor_fecha_fin) or str(valor_fecha_fin).strip() in ["", "-", "--"]:
                continue
            fecha_fin = pd.to_datetime(valor_fecha_fin)

            # Normaliza fechas (sin microsegundos y naive)
            fecha_inicio = make_naive(fecha_inicio.replace(microsecond=0))
            fecha_fin = make_naive(fecha_fin.replace(microsecond=0))

            if idx_estacion is not None:
                try:
                    estacion = Estacion.objects.get(nombre__icontains=estacion_nombre)
                except Estacion.DoesNotExist:
                    resumen.append(f"Estación no encontrada: {estacion_nombre}")
                    continue
            else:
                estacion = None  # O manejar según el contexto

            # Verificar duplicado
            if EventoImportado.objects.filter(
                estacion=estacion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            ).exists():
                duplicados += 1
                duplicados_detalle.append(f"{estacion_nombre}: {fecha_inicio} - {fecha_fin}")
                continue

            # Registrar evento importado
            EventoImportado.objects.create(
                estacion=estacion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                descripcion=evento
            )

            duracion_horas = round((fecha_fin - fecha_inicio).total_seconds() / 3600, 2)
            dia = fecha_inicio.day
            dias_mes = monthrange(anio, mes)[1]
            semana = min(4, math.ceil(dia / (dias_mes / 4)))

            try:
                gestion = GestionEstacion.objects.get(estacion=estacion, mes=mes, anio=anio)
            except GestionEstacion.DoesNotExist:
                resumen.append(f"Gestión no encontrada para {estacion_nombre} ({mes}/{anio})")
                continue

            if semana == 1:
                gestion.horas_trabajo_w19 = (gestion.horas_trabajo_w19 or 0) + duracion_horas
            elif semana == 2:
                gestion.horas_trabajo_w20 = (gestion.horas_trabajo_w20 or 0) + duracion_horas
            elif semana == 3:
                gestion.horas_trabajo_w21 = (gestion.horas_trabajo_w21 or 0) + duracion_horas
            elif semana == 4:
                gestion.horas_trabajo_w22 = (gestion.horas_trabajo_w22 or 0) + duracion_horas
            gestion.save()
            nuevos += 1
            resumen.append(f"{estacion_nombre}: +{duracion_horas} hrs a semana {semana}")

        msg = f"Importación completada. {nuevos} registros nuevos"
        if duplicados:
            msg += f", {duplicados} duplicados ignorados"
            resumen.append("Duplicados omitidos:")
            resumen.extend(duplicados_detalle)
        return JsonResponse({'success': True, 'message': msg, 'resumen': resumen})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def importar_horas_trabajo_detalle(request):
    """
    Importa horas de trabajo desde un archivo Excel para una gestión específica.
    Registra en historico_alarmas la auditoría de la importación.
    Evita duplicados por estación, fecha_inicio y fecha_fin.
    """
    file = request.FILES.get('file')
    gestion_id = request.POST.get('gestion_id')
    if not file or not gestion_id:
        return JsonResponse({'success': False, 'message': 'Archivo o gestión no especificados.'}, status=400)
    try:
        from .models import GestionEstacion, EventoImportado
        gestion = GestionEstacion.objects.get(id=gestion_id)
        df = pd.read_excel(file)
        cols = [c.lower().strip() for c in df.columns]
        eventos_importados = []
        duplicados = 0
        # Reconocer encabezados Occurrence Time y Clear Time
        resumen = []
        if set(['occurrence time', 'clear time']).issubset(set(cols)):
            idx_inicio = cols.index('occurrence time')
            idx_fin = cols.index('clear time')
            idx_evento = None  # No hay evento, se pone uno genérico
        elif set(['evento', 'inicio', 'fin']).issubset(set(cols)):
            idx_evento = cols.index('evento')
            idx_inicio = cols.index('inicio')
            idx_fin = cols.index('fin')
        elif len(cols) >= 4 and 'motogenerador' in cols[1]:
            idx_evento, idx_inicio, idx_fin = 1, 2, 3
        elif len(cols) >= 5 and 'motogenerador' in cols[1]:
            idx_evento, idx_inicio, idx_fin = 1, 3, 4
        else:
            return JsonResponse({'success': False, 'message': 'Formato de archivo no reconocido.'}, status=400)
        for _, row in df.iterrows():
            if idx_evento is not None:
                evento = str(row[idx_evento])
            else:
                evento = "Motogenerador (importado Occurrence Time)"
            fecha_inicio = pd.to_datetime(row[idx_inicio])
            fecha_fin = pd.to_datetime(row[idx_fin])
            # Normaliza fechas (sin microsegundos y naive)
            from django.utils.timezone import make_naive, is_aware
            fecha_inicio = fecha_inicio.replace(microsecond=0, second=0)
            fecha_fin = fecha_fin.replace(microsecond=0, second=0)
            if is_aware(fecha_inicio):
                fecha_inicio = make_naive(fecha_inicio)
            if is_aware(fecha_fin):
                fecha_fin = make_naive(fecha_fin)
            estacion = gestion.estacion
            # Verificar duplicado (mostrar valores en el resumen)
            existe = EventoImportado.objects.filter(
                estacion=estacion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            ).exists()
            if existe:
                duplicados += 1
                # duplicados_detalle.append(
                #     f"Duplicado: {estacion.nombre} {fecha_inicio} - {fecha_fin}"
                # )
                continue
            # Registrar evento importado
            EventoImportado.objects.create(
                estacion=estacion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                descripcion=evento
            )
            duracion_horas = round((fecha_fin - fecha_inicio).total_seconds() / 3600, 2)
            dia = fecha_inicio.day
            mes = gestion.mes or fecha_inicio.month
            anio = gestion.anio or fecha_inicio.year
            from calendar import monthrange
            dias_mes = monthrange(anio, mes)[1]
            semana = min(4, math.ceil(dia / (dias_mes / 4)))
            if semana == 1:
                gestion.horas_trabajo_w19 = (gestion.horas_trabajo_w19 or 0) + duracion_horas
            elif semana == 2:
                gestion.horas_trabajo_w20 = (gestion.horas_trabajo_w20 or 0) + duracion_horas
            elif semana == 3:
                gestion.horas_trabajo_w21 = (gestion.horas_trabajo_w21 or 0) + duracion_horas
            elif semana == 4:
                gestion.horas_trabajo_w22 = (gestion.horas_trabajo_w22 or 0) + duracion_horas
            resumen.append(f"+{duracion_horas} hrs a semana {semana}")
            eventos_importados.append(f"{evento} ({fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')} - {fecha_fin.strftime('%Y-%m-%d %H:%M:%S')}, {duracion_horas} hrs, Semana {semana})")
        # Auditoría: registrar en historico_alarmas
        now_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        auditoria = f"Importación de alarmas el {now_str}:\n" + "\n".join(eventos_importados)
        if hasattr(gestion, 'historico_alarmas') and gestion.historico_alarmas:
            gestion.historico_alarmas += "\n\n" + auditoria
        else:
            gestion.historico_alarmas = auditoria
        gestion.save()
        if duplicados:
            resumen.append(f"Cantidad de duplicados omitidos: {duplicados}")
            # resumen.extend(duplicados_detalle)
        return JsonResponse({'success': True, 'message': 'Importación completada.', 'resumen': resumen})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_POST
def importar_horas_trabajo_pegar(request):
    """
    Importa horas de trabajo desde texto pegado (copiado de Excel o archivo de texto).
    Cada línea debe tener los campos separados por tabulador o por varios espacios.
    """
    texto = request.POST.get('texto')
    gestion_id = request.POST.get('gestion_id')
    if not texto or not gestion_id:
        return JsonResponse({'success': False, 'message': 'Texto o gestión no especificados.'}, status=400)
    try:
        from .models import GestionEstacion, EventoImportado
        gestion = GestionEstacion.objects.get(id=gestion_id)
        resumen = []
        duplicados = 0
        duplicados_detalle = []
        eventos_importados = []
        import re
        for linea in texto.splitlines():
            if not linea.strip():
                continue
            # Separar por tabulador o por dos o más espacios
            if '\t' in linea:
                partes = [p.strip() for p in linea.split('\t')]
            else:
                partes = re.split(r'\s{2,}', linea.strip())
            # Si aún hay pocos campos, intenta por un solo espacio (último recurso)
            if len(partes) < 2:
                partes = linea.strip().split()
            # Permitir dos columnas: solo fechas (inicio y fin)
            if len(partes) == 2:
                evento = "Motogenerador (importado pegado)"
                try:
                    from dateutil import parser
                    fecha_inicio = parser.parse(partes[0], dayfirst=False)
                    fecha_fin = parser.parse(partes[1], dayfirst=False)
                except Exception:
                    continue
            # Si hay 4 o más columnas, usar evento y fechas
            elif len(partes) >= 4:
                evento = partes[1]
                try:
                    from dateutil import parser
                    fecha_inicio = parser.parse(partes[2], dayfirst=False)
                    fecha_fin = parser.parse(partes[3], dayfirst=False)
                except Exception:
                    continue
            else:
                continue  # línea inválida

            # Normaliza fechas
            from django.utils.timezone import make_naive, is_aware
            fecha_inicio = fecha_inicio.replace(microsegundo=0, second=0)
            fecha_fin = fecha_fin.replace(microsegundo=0, second=0)
            if is_aware(fecha_inicio):
                fecha_inicio = make_naive(fecha_inicio)
            if is_aware(fecha_fin):
                fecha_fin = make_naive(fecha_fin)
            estacion = gestion.estacion
            # Verificar duplicado (mostrar valores en el resumen)
            existe = EventoImportado.objects.filter(
                estacion=estacion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            ).exists()
            if existe:
                duplicados += 1
                # duplicados_detalle.append(
                #     f"Duplicado: {estacion.nombre} {fecha_inicio} - {fecha_fin}"
                # )
                continue
            # Registrar evento importado
            EventoImportado.objects.create(
                estacion=estacion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                descripcion=evento
            )
            duracion_horas = round(((fecha_fin - fecha_inicio).total_seconds() / 3600), 2)
            dia = fecha_inicio.day
            mes = gestion.mes or fecha_inicio.month
            anio = gestion.anio or fecha_inicio.year
            from calendar import monthrange
            dias_mes = monthrange(anio, mes)[1]
            semana = min(4, math.ceil(dia / (dias_mes / 4)))
            if semana == 1:
                gestion.horas_trabajo_w19 = (gestion.horas_trabajo_w19 or 0) + duracion_horas
            elif semana == 2:
                gestion.horas_trabajo_w20 = (gestion.horas_trabajo_w20 or 0) + duracion_horas
            elif semana == 3:
                gestion.horas_trabajo_w21 = (gestion.horas_trabajo_w21 or 0) + duracion_horas
            elif semana == 4:
                gestion.horas_trabajo_w22 = (gestion.horas_trabajo_w22 or 0) + duracion_horas
            resumen.append(f"+{duracion_horas} hrs a semana {semana}")
            eventos_importados.append(f"{evento} ({fecha_inicio.strftime('%Y-%m-%d %H:%M:%S')} - {fecha_fin.strftime('%Y-%m-%d %H:%M:%S')}, {duracion_horas} hrs, Semana {semana})")
        # Auditoría: registrar en historico_alarmas
        from django.utils import timezone
        now_str = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
        auditoria = f"Importación de alarmas (pegado) el {now_str}:\n" + "\n".join(eventos_importados)
        if hasattr(gestion, 'historico_alarmas') and gestion.historico_alarmas:
            gestion.historico_alarmas += "\n\n" + auditoria
        else:
            gestion.historico_alarmas = auditoria
        gestion.save()
        if duplicados:
            resumen.append(f"Cantidad de duplicados omitidos: {duplicados}")
            # resumen.extend(duplicados_detalle)
        return JsonResponse({'success': True, 'message': 'Importación completada.', 'resumen': resumen})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

from django.views.decorators.http import require_POST
from django.utils.safestring import mark_safe

@csrf_exempt
@require_POST
def importar_horas_masivo(request):
    """
    Importa horas de trabajo desde un archivo Excel con múltiples estaciones.
    Mapea usando EstacionMapping, nombre normalizado o id_externo.
    Devuelve una previsualización HTML para confirmar la importación.
    """
    file = request.FILES.get('file')
    mes = int(request.POST.get('mes'))
    anio = int(request.POST.get('anio'))
    if not file:
        return JsonResponse({'success': False, 'message': 'No se envió archivo.'}, status=400)
    try:
        df = pd.read_excel(file)
        cols = [c.lower().strip() for c in df.columns]
        # Detectar columnas de estación, fechas y evento
        nombre_col = None
        id_col = None
        inicio_col = None
        fin_col = None
        evento_col = None

        # NUEVO: Soporte para formato "MO Name, Name, Alarm ID, Occurred On (NT), Cleared On (NT), Alarm Duration"
        if 'mo name' in cols and 'occurred on (nt)' in cols and 'cleared on (nt)' in cols:
            nombre_col = cols.index('mo name')
            evento_col = cols.index('name') if 'name' in cols else None
            inicio_col = cols.index('occurred on (nt)')
            fin_col = cols.index('cleared on (nt)')
            # id_col = cols.index('alarm id') if 'alarm id' in cols else None
            id_col = None  # Ignorar Alarm ID como id_externo en este formato
        else:
            # ...existing detection logic...
            for i, c in enumerate(cols):
                if c in ['me', 'estacion', 'nombre estacion', 'nombre']:
                    nombre_col = i
                elif c in ['id', 'id estacion', 'id_externo']:
                    id_col = i
                elif c in ['occurrence time', 'inicio', 'fecha inicio']:
                    inicio_col = i
                elif c in ['clear time', 'fin', 'fecha fin']:
                    fin_col = i
                elif c in ['evento', 'descripcion', 'alarma', 'alarm code name']:
                    evento_col = i

        if inicio_col is None or fin_col is None or nombre_col is None:
            return JsonResponse({'success': False, 'message': 'No se detectaron columnas de estación o fechas.'}, status=400)

        # Previsualización de resultados
        preview_rows = []
        resumen = []
        filas_importables = []
        for _, row in df.iterrows():
            nombre_externo = str(row[nombre_col]).strip() if nombre_col is not None else ""
            # Extraer nombre base e id externo del nombre_externo
            nombre_base, id_extraido = extraer_nombre_id_estacion(nombre_externo)
            # Usar id_col si existe, si no, usar id_extraido
            # Solo usar id_col si no es el formato con "Alarm ID"
            if id_col is not None:
                id_externo = str(row[id_col]).strip() if not pd.isna(row[id_col]) else id_extraido
            else:
                id_externo = id_extraido
            # CORREGIDO: Sintaxis del evento
            evento = str(row[evento_col]).strip() if evento_col is not None else "Motogenerador (importado masivo)"
            fecha_inicio = pd.to_datetime(row[inicio_col])
            # IGNORAR registros sin fecha de fin válida
            valor_fecha_fin = row[fin_col]
            if pd.isna(valor_fecha_fin) or str(valor_fecha_fin).strip() in ["", "-", "--"]:
                continue
            fecha_fin = pd.to_datetime(valor_fecha_fin)
            estacion = buscar_estacion(nombre_externo, id_externo)
            if estacion:
                try:
                    gestion = GestionEstacion.objects.get(estacion=estacion, mes=mes, anio=anio)
                    gestion_id = gestion.id
                except GestionEstacion.DoesNotExist:
                    gestion = None
                    gestion_id = ""
            else:
                gestion = None
                gestion_id = ""
            preview_rows.append({
                'nombre_externo': nombre_externo,
                'id_externo': id_externo or "",
                'evento': evento,
                'fecha_inicio': fecha_inicio,
                'fecha_fin': fecha_fin,
                'estacion': estacion.nombre if estacion else "NO ENCONTRADA",
                'gestion_id': gestion_id,
                'puede_importar': bool(estacion and gestion)
            })
            if estacion and gestion:
                filas_importables.append({
                    'gestion_id': gestion_id,
                    'fecha_inicio': str(fecha_inicio),
                    'fecha_fin': str(fecha_fin),
                    'evento': evento
                })

        # Generar tabla HTML de previsualización
        table_html = """
        <div class="overflow-x-auto">
        <table class="min-w-full text-xs text-gray-700 divide-y divide-gray-200 border">
            <thead>
                <tr class="bg-blue-100 text-blue-700 uppercase tracking-wider">
                    <th class="py-2 px-2">Estación (archivo)</th>
                    <th class="py-2 px-2">ID (archivo)</th>
                    <th class="py-2 px-2">Evento</th>
                    <th class="py-2 px-2">Inicio</th>
                    <th class="py-2 px-2">Fin</th>
                    <th class="py-2 px-2">Estación (sistema)</th>
                    <th class="py-2 px-2">¿Importable?</th>
                </tr>
            </thead>
            <tbody>
        """
        for r in preview_rows:
            table_html += f"""
                <tr class="{'bg-green-50' if r['puede_importar'] else 'bg-red-50'}">
                    <td class="py-1 px-2">{r['nombre_externo']}</td>
                    <td class="py-1 px-2">{r['id_externo']}</td>
                    <td class="py-1 px-2">{r['evento']}</td>
                    <td class="py-1 px-2">{r['fecha_inicio']}</td>
                    <td class="py-1 px-2">{r['fecha_fin']}</td>
                    <td class="py-1 px-2">{r['estacion']}</td>
                    <td class="py-1 px-2">{'Sí' if r['puede_importar'] else 'No'}</td>
                </tr>
            """
        table_html += "</tbody></table></div>"
        resumen.append(f"Total registros: {len(preview_rows)}")
        resumen.append(f"Importables: {sum(1 for r in preview_rows if r['puede_importar'])}")
        resumen.append(f"No importables: {sum(1 for r in preview_rows if not r['puede_importar'])}")

        return JsonResponse({
            'success': True,
            'preview_html': mark_safe(table_html),
            'resumen': resumen,
            'filas_importables': filas_importables  # <-- Agrega esto
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def extraer_nombre_id_estacion(nombre_externo):
    """
    Extrae el nombre base y el id externo de una cadena tipo 'San_Telmo(5721)'.
    Devuelve (nombre_base, id_externo) o (nombre_externo, None) si no hay paréntesis.
    """
    match = re.match(r'^(.*?)[\(\[](\d+)[\)\]]$', nombre_externo.strip())
    if match:
        nombre_base = match.group(1).replace("_", " ").replace("-", " ").strip()
        id_externo = match.group(2)
        return nombre_base, id_externo
    # Si no hay paréntesis, devolver el nombre tal cual y None
    return nombre_externo.strip(), None

def buscar_estacion(nombre_externo, id_externo=None):
    # 1. Extraer nombre base e id si viene en formato 'San_Telmo(5721)'
    nombre_base, id_extraido = extraer_nombre_id_estacion(nombre_externo)
    nombre_norm = normalizar_nombre(nombre_base)
    # 2. Buscar en el mapping por nombre_externo exacto
    mapping = EstacionMapping.objects.filter(nombre_externo__iexact=nombre_externo)
    if not mapping and id_externo:
        mapping = EstacionMapping.objects.filter(id_externo=id_externo)
    if not mapping and id_extraido:
        mapping = EstacionMapping.objects.filter(id_externo=id_extraido)
    if not mapping:
        # Buscar por nombre base en mapping
        mapping = EstacionMapping.objects.filter(nombre_externo__iexact=nombre_base)
    if mapping.exists():
        return mapping.first().estacion
    # 3. Buscar por id_externo en Estacion
    if id_externo:
        estacion = Estacion.objects.filter(estacion_id=id_externo).first()
        if estacion:
            return estacion
    if id_extraido:
        estacion = Estacion.objects.filter(estacion_id=id_extraido).first()
        if estacion:
            return estacion
    # 4. Buscar por nombre normalizado en Estacion
    for estacion in Estacion.objects.all():
        if normalizar_nombre(estacion.nombre) == nombre_norm:
            return estacion
    return None

@csrf_exempt
@require_POST
def confirmar_importar_horas_masivo(request):
    """
    Recibe los datos validados de la previsualización y realiza la importación real de horas.
    Espera un JSON con las filas a importar.
    """
    try:
        data = json.loads(request.body)
        filas = data.get('filas', [])
        mes = int(data.get('mes'))
        anio = int(data.get('anio'))
        resumen = []
        nuevos = 0
        duplicados = 0

        for fila in filas:
            gestion_id = fila.get('gestion_id')
            fecha_inicio = pd.to_datetime(fila.get('fecha_inicio'))
            fecha_fin = pd.to_datetime(fila.get('fecha_fin'))
            evento = fila.get('evento', 'Motogenerador (importado masivo)')
            if not gestion_id:
                continue
            try:
                gestion = GestionEstacion.objects.get(id=gestion_id)
            except GestionEstacion.DoesNotExist:
                resumen.append(f"Gestión no encontrada para ID {gestion_id}")
                continue

            estacion = gestion.estacion

            # Verificar duplicado
            if EventoImportado.objects.filter(
                estacion=estacion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin
            ).exists():
                duplicados += 1
                continue

            # Registrar evento importado
            EventoImportado.objects.create(
                estacion=estacion,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                descripcion=evento
            )

            duracion_horas = round((fecha_fin - fecha_inicio).total_seconds() / 3600, 2)
            dia = fecha_inicio.day
            dias_mes = monthrange(anio, mes)[1]
            semana = min(4, math.ceil(dia / (dias_mes / 4)))

            if semana == 1:
                gestion.horas_trabajo_w19 = (gestion.horas_trabajo_w19 or 0) + duracion_horas
            elif semana == 2:
                gestion.horas_trabajo_w20 = (gestion.horas_trabajo_w20 or 0) + duracion_horas
            elif semana == 3:
                gestion.horas_trabajo_w21 = (gestion.horas_trabajo_w21 or 0) + duracion_horas
            elif semana == 4:
                gestion.horas_trabajo_w22 = (gestion.horas_trabajo_w22 or 0) + duracion_horas
            gestion.save()
            nuevos += 1
            resumen.append(f"{estacion.nombre}: +{duracion_horas} hrs a semana {semana}")

        msg = f"Importación completada. {nuevos} registros nuevos"
        if duplicados:
            msg += f", {duplicados} duplicados ignorados"
        return JsonResponse({'success': True, 'message': msg, 'resumen': resumen})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@login_required
def historico_alertas(request):
    """
    Muestra todos los eventos importados (horas de trabajo) con filtro por nombre de estación.
    """
    filtro = request.GET.get('q', '').strip()
    eventos = EventoImportado.objects.select_related('estacion').order_by('-fecha_inicio')
    if filtro:
        eventos = eventos.filter(estacion__nombre__icontains=filtro)
    paginator = Paginator(eventos, 50)  # 50 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # Calcular duración en horas para cada evento
    for evento in page_obj:
        if evento.fecha_inicio and evento.fecha_fin:
            evento.duracion_horas = round((evento.fecha_fin - evento.fecha_inicio).total_seconds() / 3600, 2)
        else:
            evento.duracion_horas = ""
    return render(request, 'gestion/historico_alertas.html', {
        'eventos': page_obj,
        'filtro': filtro,
    })

@csrf_exempt
def comentarios_gestion(request, gestion_id):
    """
    GET: Lista comentarios.
    POST: Añade comentario.
    PUT: Edita comentario.
    DELETE: Elimina comentario.
    Soporta ?tipo=tanques para comentarios exclusivos de tanques.
    """
    tipo = request.GET.get('tipo', '').strip().lower()
    filtro_tipo = {'tipo': 'tanques'} if tipo == 'tanques' else {'tipo': 'general'}
    if request.method == 'GET':
        comentarios = ComentarioGestion.objects.filter(gestion_id=gestion_id, **filtro_tipo).order_by('-fecha')
        data = [
            {"id": c.id, "texto": c.texto, "fecha": c.fecha.strftime("%Y-%m-%d %H:%M"), "autor": c.autor or ""}
            for c in comentarios
        ]
        return JsonResponse({"success": True, "comentarios": data})

    elif request.method == 'POST':
        body = json.loads(request.body)
        texto = body.get("texto", "").strip()
        autor = body.get("autor", "")
        if not texto:
            return JsonResponse({"success": False, "message": "El comentario no puede estar vacío."})
        comentario = ComentarioGestion.objects.create(
            gestion_id=gestion_id, texto=texto, autor=autor, tipo='tanques' if tipo == 'tanques' else 'general'
        )
        return JsonResponse({"success": True, "comentario": {
            "id": comentario.id,
            "texto": comentario.texto,
            "fecha": comentario.fecha.strftime("%Y-%m-%d %H:%M"),
            "autor": comentario.autor or ""
        }})

    elif request.method == 'PUT':
        body = json.loads(request.body)
        comentario_id = body.get("id")
        texto = body.get("texto", "").strip()
        if not comentario_id or not texto:
            return JsonResponse({"success": False, "message": "Datos incompletos."})
        try:
            comentario = ComentarioGestion.objects.get(id=comentario_id, gestion_id=gestion_id, **filtro_tipo)
            comentario.texto = texto
            comentario.save()
            return JsonResponse({"success": True})
        except ComentarioGestion.DoesNotExist:
            return JsonResponse({"success": False, "message": "Comentario no encontrado."})

    elif request.method == 'DELETE':
        body = json.loads(request.body)
        comentario_id = body.get("id")
        try:
            comentario = ComentarioGestion.objects.get(id=comentario_id, gestion_id=gestion_id, **filtro_tipo)
            comentario.delete()
            return JsonResponse({"success": True})
        except ComentarioGestion.DoesNotExist:
            return JsonResponse({"success": False, "message": "Comentario no encontrado."})

    return JsonResponse({"success": False, "message": "Método no permitido."}, status=405)

@csrf_exempt
def actualizar_semana_gestion(request, gestion_id):
    """
    Actualiza el suministro y las horas de trabajo de una semana específica de una gestión.
    """
    try:
        data = json.loads(request.body)
        semana = int(data.get("semana"))
        suministro = float(data.get("suministro", 0))
        horas_trabajo = float(data.get("horas_trabajo", 0))
        gestion = GestionEstacion.objects.get(id=gestion_id)
        if semana == 19:
            gestion.suministro_w19 = suministro
            gestion.horas_trabajo_w19 = horas_trabajo
            promedio = gestion.calcular_promedio_diario(horas_trabajo)
        elif semana == 20:
            gestion.suministro_w20 = suministro
            gestion.horas_trabajo_w20 = horas_trabajo
            promedio = gestion.calcular_promedio_diario(horas_trabajo)
        elif semana == 21:
            gestion.suministro_w21 = suministro
            gestion.horas_trabajo_w21 = horas_trabajo
            promedio = gestion.calcular_promedio_diario(horas_trabajo)
        elif semana == 22:
            gestion.suministro_w22 = suministro
            gestion.horas_trabajo_w22 = horas_trabajo
            promedio = gestion.calcular_promedio_diario(horas_trabajo)
        elif semana == 23:
            gestion.suministro_w23 = suministro
            gestion.horas_trabajo_w23 = horas_trabajo
            promedio = gestion.calcular_promedio_diario(horas_trabajo)
        else:
            return JsonResponse({"success": False, "message": "Semana inválida"})
        gestion.save()
        registrar_evento_auditoria(request, "Editar", "Gestiones", f"Actualizó semana {semana} de gestión {gestion_id}: suministro={suministro}, horas_trabajo={horas_trabajo}")
        return JsonResponse({"success": True, "promedio_diario": promedio})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

@csrf_exempt
@require_POST
def actualizar_observaciones_gestion(request, gestion_id):
    """
    Actualiza las observaciones de una gestión (añade comentario).
    """
    try:
        data = json.loads(request.body)
        texto = data.get("observacion", "").strip()
        if not texto:
            return JsonResponse({"success": False, "message": "El comentario no puede estar vacío."})
        gestion = GestionEstacion.objects.get(id=gestion_id)
        if gestion.observaciones:
            gestion.observaciones += "\n" + texto
        else:
            gestion.observaciones = texto
        gestion.save()
        registrar_evento_auditoria(request, "Editar", "Gestiones", f"Actualizó observaciones gestión {gestion_id}")
        return JsonResponse({"success": True, "observaciones": gestion.observaciones})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})

@csrf_exempt
@login_required
def toggle_tanque_reserva(request, estacion_id):
    if request.method == "POST":
        try:
            estacion = Estacion.objects.get(id=estacion_id)
            estacion.tanque_reserva_condenado = not estacion.tanque_reserva_condenado
            estacion.save()
            return JsonResponse({"success": True, "condenado": estacion.tanque_reserva_condenado})
        except Exception:
            return JsonResponse({"success": False})
    return JsonResponse({"success": False})

@csrf_exempt
@login_required
def toggle_tanque_base(request, estacion_id):
    if request.method == "POST":
        try:
            estacion = Estacion.objects.get(id=estacion_id)
            estacion.tanque_base_condenado = not estacion.tanque_base_condenado
            estacion.save()
            return JsonResponse({"success": True, "condenado": estacion.tanque_base_condenado})
        except Exception:
            return JsonResponse({"success": False})
    return JsonResponse({"success": False})

@csrf_exempt
@login_required
def toggle_tanque_externo(request, estacion_id):
    if request.method == "POST":
        try:
            estacion = Estacion.objects.get(id=estacion_id)
            estacion.tanque_externo_condenado = not estacion.tanque_externo_condenado
            estacion.save()
            return JsonResponse({"success": True, "condenado": estacion.tanque_externo_condenado})
        except Exception:
            return JsonResponse({"success": False})
    return JsonResponse({"success": False})

def exportar_gestiones(request, formato):
    """
    Exporta todas las columnas del modelo GestionEstacion y campos relevantes de Estacion.
    Ahora usa los mismos nombres de columna que espera el importador.
    """
    mes = int(request.GET.get('mes', date.today().month))
    anio = int(request.GET.get('anio', date.today().year))
    gestiones = GestionEstacion.objects.filter(mes=mes, anio=anio).select_related('estacion')

    # Nombres de columna para exportar (idénticos a los que espera el importador)
    columnas = [
        "ID", "REGIÓN", "MERCADO", "NOMBRE", "COMSUMO", "TANQUE BASE", "TANQUE EXTERNO", "TOTAL", "CAPACIDAD ANTERIOR",
        "DISPONIBLE (LTS)", "NIVEL", "PORCENTAJE", "HRS TOTAL", "HRS PROMEDIO MENSUAL", "AUTONOMÍA HRS", "NECESARIO PARA 100%",
        "24 HRS (VACIO)", "24 HRS (REAL)", "36 HRS (VACIO)", "36 HRS (REAL)", "48 HRS (VACIO)", "48 HRS (REAL)",
        "72 HRS (VACIO)", "72 HRS (REAL)", "96 HRS (VACIO)", "96 HRS (REAL)", "OBSERVACIONES",
        "SUMINISTRO W19", "HRS TRABAJO W19", "PROMEDIO DIARIO W19",
        "SUMINISTRO W20", "HRS TRABAJO W20", "PROMEDIO DIARIO W20",
        "SUMINISTRO W21", "HRS TRABAJO W21", "PROMEDIO DIARIO W21",
        "SUMINISTRO W22", "HRS TRABAJO W22", "PROMEDIO DIARIO W22",
        "SUMINISTRO W23", "HRS TRABAJO W23", "PROMEDIO DIARIO W23",
    ]

    def fila_gestion(g):
        e = g.estacion
        return [
            e.estacion_id if e else "",
            e.region if e else "",
            e.mercado if e else "",
            e.nombre if e else "",
            e.consumo if e else "",
            e.tanque_base if e else "",
            e.tanque_externo if e else "",
            e.total if e else "",
            e.capacidad_anterior if e else "",
            g.disponible or "",
            g.nivel_combustible or "",
            g.porcentaje or "",
            g.hrs_total or "",
            g.hrs_promedio_mensual or "",
            g.autonomia_hrs or "",
            g.necesario_100 or "",
            g.vacio_24 or "",
            g.real_24 or "",
            g.vacio_36 or "",
            g.real_36 or "",
            g.vacio_48 or "",
            g.real_48 or "",
            g.vacio_72 or "",
            g.real_72 or "",
            g.vacio_96 or "",
            g.real_96 or "",
            g.observaciones or "",
            g.suministro_w19 or "",
            g.horas_trabajo_w19 or "",
            g.promedio_diario_w19 or "",
            g.suministro_w20 or "",
            g.horas_trabajo_w20 or "",
            g.promedio_diario_w20 or "",
            g.suministro_w21 or "",
            g.horas_trabajo_w21 or "",
            g.promedio_diario_w21 or "",
            g.suministro_w22 or "",
            g.horas_trabajo_w22 or "",
            g.promedio_diario_w22 or "",
            g.suministro_w23 or "",
            g.horas_trabajo_w23 or "",
            g.promedio_diario_w23 or "",
        ]

    if formato == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="gestiones_{mes}_{anio}.csv"'
        writer = csv.writer(response)
        writer.writerow(columnas)
        for g in gestiones:
            writer.writerow(fila_gestion(g))
        return response

    elif formato == 'excel':
        import pandas as pd
        data = [dict(zip(columnas, fila_gestion(g))) for g in gestiones]
        df = pd.DataFrame(data)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        response = HttpResponse(
            output,
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename="gestiones_{mes}_{anio}.xlsx"'
        return response

    else:
        return HttpResponse("Formato no soportado.", status=400)

@csrf_exempt
def actualizar_capacidad_maxima_reserva(request, estacion_id):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            valor = data.get("capacidad_maxima_reserva")
            estacion = Estacion.objects.get(id=estacion_id)
            # Conversión robusta a float o None
            if valor in [None, '', 'null']:
                estacion.capacidad_maxima_reserva = None
            else:
                estacion.capacidad_maxima_reserva = float(valor)
            estacion.save()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "Método no permitido"})
    return JsonResponse({"success": False, "error": "Método no permitido"})
