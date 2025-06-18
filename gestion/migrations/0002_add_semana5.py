from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('gestion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gestionestacion',
            name='suministro_w23',
            field=models.FloatField(null=True, blank=True, default=0),
        ),
        migrations.AddField(
            model_name='gestionestacion',
            name='horas_trabajo_w23',
            field=models.FloatField(null=True, blank=True, default=0),
        ),
        migrations.AddField(
            model_name='gestionestacion',
            name='promedio_diario_w23',
            field=models.FloatField(null=True, blank=True, editable=False),
        ),
    ]
