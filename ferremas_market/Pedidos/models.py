from django.db import models
from Usuario.models import Cliente
from django.utils import timezone

class Categoria(models.Model):
    nombre = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=120)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

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
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.stock <= 0:
            self.activo = False
        else:
            self.activo = True
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre

class Pedido(models.Model):
    ESTADO_OPCIONES = (
        (1, 'Pendiente'),
        (2, 'En proceso'),
        (3, 'Enviado'),
        (4, 'Entregado'),
        (5, 'Cancelado')
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
        if self.estado == 3 and not self.fecha_envio:
            self.fecha_envio = timezone.now()
        super(Pedido, self).save(*args, **kwargs)

# Modelos temporales, posiblemente se deban borrar en un futuro
class Compra(models.Model):
    usuario = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='compras')
    fecha_compra = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField()

    def __str__(self):
        return f'Compra {self.id} - {self.usuario.username} - {self.fecha_compra}'

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.IntegerField()

    def __str__(self):
        return f'{self.producto.nombre} x {self.cantidad}'