from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0006_remove_gestionestacion_capacidad_anterior_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gestionestacion',
            name='mes',
            field=models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Mes'),
        ),
        migrations.AddField(
            model_name='gestionestacion',
            name='anio',
            field=models.PositiveSmallIntegerField(null=True, blank=True, verbose_name='Año'),
        ),
    ]
