# Generated by Django 5.0.4 on 2024-05-23 06:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Usuario', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TipoComunicacion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('descripcion', models.CharField(max_length=120)),
                ('foto', models.ImageField(blank=True, upload_to='tipo_comunicacion/%Y/%m/%d/')),
            ],
        ),
        migrations.CreateModel(
            name='Suscripcion',
            fields=[
                ('cliente', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='suscripcion', serialize=False, to='Usuario.cliente')),
                ('activo', models.BooleanField(default=True)),
                ('fecha_registro', models.DateTimeField(auto_now_add=True)),
                ('tipo_comunicacion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suscripciones', to='Comunicacion.tipocomunicacion')),
            ],
        ),
    ]
