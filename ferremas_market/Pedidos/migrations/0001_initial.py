# Generated by Django 5.0.4 on 2024-05-11 22:51

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('Usuario', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Carrito',
            fields=[
                ('run', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='pedido', serialize=False, to='Usuario.cliente')),
                ('fecha_creacion', models.DateTimeField(auto_now_add=True)),
                ('hora_actualizado', models.DateTimeField(auto_now=True)),
                ('activo', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('descripcion', models.CharField(max_length=120)),
                ('precio', models.IntegerField()),
                ('stock', models.IntegerField()),
                ('foto', models.ImageField(blank=True, upload_to='producto/%Y/%m/%d/')),
            ],
        ),
        migrations.CreateModel(
            name='Pedido',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('estado', models.IntegerField(choices=[(1, 'Pendiente'), (2, 'En proceso'), (3, 'Enviado'), (4, 'Entregado')], default=1)),
                ('informacion_adicional', models.CharField(max_length=120)),
                ('fecha_recivo', models.DateTimeField(auto_now_add=True)),
                ('fecha_envio', models.DateTimeField()),
                ('activo', models.BooleanField(default=True)),
                ('run', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pedidos', to='Usuario.cliente')),
            ],
        ),
        migrations.CreateModel(
            name='ProductoCarrito',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cantidad', models.IntegerField()),
                ('carrito', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos_carrito', to='Pedidos.carrito')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='productos_carrito', to='Pedidos.producto')),
            ],
        ),
    ]
