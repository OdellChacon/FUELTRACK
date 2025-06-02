import pandas as pd
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from estaciones.models import Estacion
from .models import GestionEstacion
import datetime

def get_val(row, key, default=0):
    val = row.get(key, default)
    if pd.isna(val) or val is None:
        return default
    return val

@login_required
@csrf_exempt
def importar_gestiones(request):
    if request.method == "POST" and request.FILES.get("file"):
        file = request.FILES["file"]
        df = pd.read_excel(file)
        # Obtén mes y año del request (GET o POST), si existen
        mes_actual = int(request.GET.get("mes") or request.POST.get("mes") or datetime.date.today().month)
        anio_actual = int(request.GET.get("anio") or request.POST.get("anio") or datetime.date.today().year)
        # Mapeo de columnas Excel a campos del modelo
        for _, row in df.iterrows():
            estacion_id = int(get_val(row, "ID"))
            estacion, _ = Estacion.objects.get_or_create(
                id=estacion_id,
                defaults={
                    "region": get_val(row, "REGIÓN", ""),
                    "mercado": get_val(row, "MERCADO", ""),
                    "nombre": get_val(row, "NOMBRE", ""),
                    "consumo": get_val(row, "COMSUMO"),
                    "tanque_base": get_val(row, "TANQUE BASE"),
                    "tanque_externo": get_val(row, "TANQUE EXTERNO"),
                    "total": get_val(row, "TOTAL"),
                    "capacidad_anterior": get_val(row, "CAPACIDAD ANTERIOR"),
                }
            )
            # Actualiza datos de estación si ya existe
            estacion.region = get_val(row, "REGIÓN", "")
            estacion.mercado = get_val(row, "MERCADO", "")
            estacion.nombre = get_val(row, "NOMBRE", "")
            estacion.consumo = get_val(row, "COMSUMO")
            estacion.tanque_base = get_val(row, "TANQUE BASE")
            estacion.tanque_externo = get_val(row, "TANQUE EXTERNO")
            estacion.total = get_val(row, "TOTAL")
            estacion.capacidad_anterior = get_val(row, "CAPACIDAD ANTERIOR")
            estacion.save()

            gestion, _ = GestionEstacion.objects.get_or_create(
                estacion=estacion,
                semana="IMPORT",
                mes=mes_actual,
                anio=anio_actual,
                defaults={
                    "disponible": get_val(row, "DISPONIBLE (LTS)"),
                    "nivel_combustible": get_val(row, "NIVEL"),
                    "porcentaje": float(str(get_val(row, "PORCENTAJE", 0)).replace("%", "")) if get_val(row, "PORCENTAJE", 0) else 0,
                    "suministro_w19": get_val(row, "SUMINISTRO W19"),
                    "horas_trabajo_w19": get_val(row, "HRS TRABAJO W19"),
                    "promedio_diario_w19": get_val(row, "PROMEDIO DIARIO W19"),
                    "suministro_w20": get_val(row, "SUMINISTRO W20"),
                    "horas_trabajo_w20": get_val(row, "HRS TRABAJO W20"),
                    "promedio_diario_w20": get_val(row, "PROMEDIO DIARIO W20"),
                    "suministro_w21": get_val(row, "SUMINISTRO W21"),
                    "horas_trabajo_w21": get_val(row, "HRS TRABAJO W21"),
                    "promedio_diario_w21": get_val(row, "PROMEDIO DIARIO W21"),
                    "suministro_w22": get_val(row, "SUMINISTRO W22"),
                    "horas_trabajo_w22": get_val(row, "HRS TRABAJO W22"),
                    "promedio_diario_w22": get_val(row, "PROMEDIO DIARIO W22"),
                    "hrs_total": get_val(row, "HRS TOTAL"),
                    "hrs_promedio_mensual": get_val(row, "HRS PROMEDIO MENSUAL"),
                    "autonomia_hrs": get_val(row, "AUTONOMÍA HRS"),
                    "necesario_100": get_val(row, "NECESARIO PARA 100%"),
                    "vacio_24": get_val(row, "24 HRS (VACIO)"),
                    "real_24": get_val(row, "24 HRS (REAL)"),
                    "vacio_36": get_val(row, "36 HRS (VACIO)"),
                    "real_36": get_val(row, "36 HRS (REAL)"),
                    "vacio_48": get_val(row, "48 HRS (VACIO)"),
                    "real_48": get_val(row, "48 HRS (REAL)"),
                    "vacio_72": get_val(row, "72 HRS (VACIO)"),
                    "real_72": get_val(row, "72 HRS (REAL)"),
                    "vacio_96": get_val(row, "96 HRS (VACIO)"),
                    "real_96": get_val(row, "96 HRS (REAL)"),
                    "observaciones": get_val(row, "OBSERVACIONES", ""),
                }
            )
            # Actualiza campos si ya existe
            gestion.disponible = get_val(row, "DISPONIBLE (LTS)")
            gestion.nivel_combustible = get_val(row, "NIVEL")
            gestion.porcentaje = float(str(get_val(row, "PORCENTAJE", 0)).replace("%", "")) if get_val(row, "PORCENTAJE", 0) else 0
            gestion.suministro_w19 = get_val(row, "SUMINISTRO W19")
            gestion.horas_trabajo_w19 = get_val(row, "HRS TRABAJO W19")
            gestion.promedio_diario_w19 = get_val(row, "PROMEDIO DIARIO W19")
            gestion.suministro_w20 = get_val(row, "SUMINISTRO W20")
            gestion.horas_trabajo_w20 = get_val(row, "HRS TRABAJO W20")
            gestion.promedio_diario_w20 = get_val(row, "PROMEDIO DIARIO W20")
            gestion.suministro_w21 = get_val(row, "SUMINISTRO W21")
            gestion.horas_trabajo_w21 = get_val(row, "HRS TRABAJO W21")
            gestion.promedio_diario_w21 = get_val(row, "PROMEDIO DIARIO W21")
            gestion.suministro_w22 = get_val(row, "SUMINISTRO W22")
            gestion.horas_trabajo_w22 = get_val(row, "HRS TRABAJO W22")
            gestion.promedio_diario_w22 = get_val(row, "PROMEDIO DIARIO W22")
            gestion.hrs_total = get_val(row, "HRS TOTAL")
            gestion.hrs_promedio_mensual = get_val(row, "HRS PROMEDIO MENSUAL")
            gestion.autonomia_hrs = get_val(row, "AUTONOMÍA HRS")
            gestion.necesario_100 = get_val(row, "NECESARIO PARA 100%")
            gestion.vacio_24 = get_val(row, "24 HRS (VACIO)")
            gestion.real_24 = get_val(row, "24 HRS (REAL)")
            gestion.vacio_36 = get_val(row, "36 HRS (VACIO)")
            gestion.real_36 = get_val(row, "36 HRS (REAL)")
            gestion.vacio_48 = get_val(row, "48 HRS (VACIO)")
            gestion.real_48 = get_val(row, "48 HRS (REAL)")
            gestion.vacio_72 = get_val(row, "72 HRS (VACIO)")
            gestion.real_72 = get_val(row, "72 HRS (REAL)")
            gestion.vacio_96 = get_val(row, "96 HRS (VACIO)")
            gestion.real_96 = get_val(row, "96 HRS (REAL)")
            gestion.observaciones = get_val(row, "OBSERVACIONES", "")
            gestion.mes = mes_actual
            gestion.anio = anio_actual
            gestion.save()
        messages.success(request, "Importación completada correctamente.")
    return redirect("lista_estaciones")
