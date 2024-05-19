from django.db import models
from Usuario.models import Cliente
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=120)
    activo = models.BooleanField(default=True)

class Producto(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.TextField()
    precio = models.IntegerField()
    stock = models.IntegerField()
    foto = models.ImageField(upload_to='producto/%Y/%m/%d/', blank=True)
    categoria = models.ForeignKey(
            Categoria,
            on_delete=models.CASCADE,
            related_name='productos',
            null=True
    )

class Carrito(models.Model):
    run = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='pedido'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    hora_actualizado = models.DateTimeField(auto_now=True)
    activo = models.BooleanField(default=True)

class ProductoCarrito(models.Model):
    carrito = models.ForeignKey(
        Carrito,
        on_delete=models.CASCADE,
        related_name='productos_carrito'
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        related_name='productos_carrito'
    )
    cantidad = models.IntegerField()

class Pedido(models.Model):
    ESTADO_OPCIONES = (
        (1, 'Pendiente'),
        (2, 'En proceso'),
        (3, 'Enviado'),
        (4, 'Entregado')
    )
    run = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    estado = models.IntegerField(choices=ESTADO_OPCIONES, default=1)
    informacion_adicional = models.CharField(max_length=120)
    fecha_recivo = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField()
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.estado == 3 and not self.fecha_envio:  # Estado 3 = 'Enviado'
            self.fecha_envio = timezone.now()
        super(Pedido, self).save(*args, **kwargs)