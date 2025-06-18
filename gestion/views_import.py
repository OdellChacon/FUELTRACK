import pandas as pd
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from estaciones.models import Estacion
from .models import GestionEstacion
from auditoria.views import registrar_evento_auditoria
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
        mes_actual = int(request.GET.get("mes") or request.POST.get("mes") or datetime.date.today().month)
        anio_actual = int(request.GET.get("anio") or request.POST.get("anio") or datetime.date.today().year)

        # --- CORREGIDO: Mapeo correcto de semanas ---
        # Buscar sufijos de semana presentes (ej: 23, 24, 25, 26)
        sufijos = []
        for col in df.columns:
            if "SUMINISTRO W" in col:
                suf = col.split("SUMINISTRO W")[-1].strip()
                if suf.isdigit():
                    sufijos.append(int(suf))
        sufijos = sorted(sufijos)[:5]  # Ahora hasta 5 semanas

        # Construir mapeo de columnas a campos w19-w23
        semanas_info = []
        for idx, suf in enumerate(sufijos):
            semana = {
                "field": f"w{19+idx}",  # w19, w20, w21, w22, w23
                "col_suministro": next((c for c in df.columns if f"SUMINISTRO W{suf}" in c), None),
                "col_horas": next((c for c in df.columns if f"HRS TRABAJO W{suf}" in c), None),
                "col_promedio": next((c for c in df.columns if f"PROMEDIO DIARIO W{suf}" in c), None),
            }
            semanas_info.append(semana)

        for _, row in df.iterrows():
            estacion_id = int(get_val(row, "ID"))
            mes = mes_actual
            anio = anio_actual
            estacion = Estacion.objects.filter(estacion_id=estacion_id).first()
            if not estacion:
                estacion = Estacion.objects.create(
                    estacion_id=estacion_id,
                    region=get_val(row, "REGIÓN", ""),
                    mercado=get_val(row, "MERCADO", ""),
                    nombre=get_val(row, "NOMBRE", ""),
                    consumo=get_val(row, "COMSUMO"),
                    tanque_base=get_val(row, "TANQUE BASE"),
                    tanque_externo=get_val(row, "TANQUE EXTERNO"),
                    total=get_val(row, "TOTAL"),
                    capacidad_anterior=get_val(row, "CAPACIDAD ANTERIOR"),
                )
            else:
                estacion.region = get_val(row, "REGIÓN", "")
                estacion.mercado = get_val(row, "MERCADO", "")
                estacion.nombre = get_val(row, "NOMBRE", "")
                estacion.consumo = get_val(row, "COMSUMO")
                estacion.tanque_base = get_val(row, "TANQUE BASE")
                estacion.tanque_externo = get_val(row, "TANQUE EXTERNO")
                estacion.total = get_val(row, "TOTAL")
                estacion.capacidad_anterior = get_val(row, "CAPACIDAD ANTERIOR")
                estacion.save()

            semanas_kwargs = {}
            for idx, semana in enumerate(semanas_info):
                suf = 19 + idx
                if semana["col_suministro"]:
                    semanas_kwargs[f"suministro_w{suf}"] = get_val(row, semana["col_suministro"])
                if semana["col_horas"]:
                    semanas_kwargs[f"horas_trabajo_w{suf}"] = get_val(row, semana["col_horas"])
                if semana["col_promedio"]:
                    semanas_kwargs[f"promedio_diario_w{suf}"] = get_val(row, semana["col_promedio"])

            gestion, _ = GestionEstacion.objects.get_or_create(
                estacion=estacion,
                semana="IMPORT",
                mes=mes_actual,
                anio=anio_actual,
                defaults={
                    "disponible": get_val(row, "DISPONIBLE (LTS)"),
                    "nivel_combustible": get_val(row, "NIVEL"),
                    "porcentaje": float(str(get_val(row, "PORCENTAJE", 0)).replace("%", "")) if get_val(row, "PORCENTAJE", 0) else 0,
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
                    **semanas_kwargs
                }
            )
            gestion.disponible = get_val(row, "DISPONIBLE (LTS)")
            gestion.nivel_combustible = get_val(row, "NIVEL")
            gestion.porcentaje = float(str(get_val(row, "PORCENTAJE", 0)).replace("%", "")) if get_val(row, "PORCENTAJE", 0) else 0
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
            for idx, semana in enumerate(semanas_info):
                suf = 19 + idx
                if semana["col_suministro"]:
                    setattr(gestion, f"suministro_w{suf}", get_val(row, semana["col_suministro"]))
                if semana["col_horas"]:
                    setattr(gestion, f"horas_trabajo_w{suf}", get_val(row, semana["col_horas"]))
                if semana["col_promedio"]:
                    setattr(gestion, f"promedio_diario_w{suf}", get_val(row, semana["col_promedio"]))
            gestion.save()
            # Registrar en auditoría la importación/actualización de cada gestión
            registrar_evento_auditoria(request, "Importar", "Gestiones", f"Importación/actualización de gestión {gestion.id} para estación {estacion.estacion_id}")
        messages.success(request, "Importación completada correctamente.")
    return redirect("lista_estaciones")
