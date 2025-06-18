from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0006_estacion'),  # Ajusta el número según tu última migración real
    ]

    operations = [
        migrations.AddField(
            model_name='gestionestacion',
            name='promedio_diario_w23',
            field=models.FloatField(null=True, blank=True, editable=False),
        ),
    ]
