# Fuel Track

Aplicación web para el control de consumo de combustible de los motogeneradores en las estaciones de telecomunicaciones de la región andina de **Telefónica Venezolana**. Desarrollada durante mi pasantía (mayo–julio 2025) para reemplazar el registro que se llevaba en planillas manuales.

## El problema

Cada estación registraba en papel las cargas de combustible y las horas de trabajo de sus motogeneradores. Consolidar esa información para saber cuánto se consumía, en qué estación y cuándo reabastecer era lento y propenso a errores.

## Qué hace

- **Estaciones:** registro de las estaciones y sus motogeneradores.
- **Gestión de cargas:** registro de cada carga de combustible y de las horas de trabajo por estación.
- **Consumo:** cálculo del porcentaje de combustible consumido para saber qué estaciones requieren abastecimiento.
- **Auditoría:** historial de las operaciones realizadas en el sistema.
- **Usuarios:** gestión de usuarios y acceso con login para el personal operativo.

## Stack

- **Backend:** Python, Django
- **Base de datos:** PostgreSQL
- **Frontend:** plantillas de Django, TailwindCSS, JavaScript
- **Control de versiones:** Git, con entregas incrementales validadas con el área usuaria

## Estructura

```
Fueltrack/     configuración del proyecto
base/          layout, login y dashboard
usuarios/      gestión de usuarios
estaciones/    estaciones y motogeneradores
gestion/       cargas de combustible y consumo
auditoria/     registro de operaciones
```

## Correr en local

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Crea la base de datos en PostgreSQL y configura las variables en .env
# (ver .env.example)

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

Desarrollado por [Odell Chacón](https://github.com/OdellChacon).
