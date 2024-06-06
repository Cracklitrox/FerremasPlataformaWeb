import uuid
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
    nombre = models.TextField()
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
        (5, 'Cancelado'),
        (6, 'Preparando despacho'),
        (7, 'En transito'),
    )
    run = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        related_name='pedidos'
    )
    estado = models.IntegerField(choices=ESTADO_OPCIONES, default=1)
    informacion_adicional = models.CharField(max_length=120)
    fecha_recivo = models.DateTimeField(blank=True, null=True)
    fecha_envio = models.DateTimeField(blank=True, null=True)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if self.estado == 3 and not self.fecha_envio:
            self.fecha_envio = timezone.now()
        super(Pedido, self).save(*args, **kwargs)

class Compra(models.Model):
    usuario = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='compras')
    fecha_compra = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField()
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    metodo_pago = models.CharField(max_length=50)
    numero_tarjeta = models.CharField(max_length=20, blank=True, null=True)
    codigo_autorizacion = models.CharField(max_length=20, blank=True, null=True)
    codigo_respuesta = models.CharField(max_length=3, blank=True, null=True)
    estado = models.CharField(max_length=20, default='Pendiente')
    numero_cuotas = models.IntegerField(null=True, blank=True)
    monto_cuota = models.FloatField(null=True, blank=True)
    fecha_autorizacion = models.CharField(max_length=5, blank=True, null=True)
    fechaHora_autorizacion = models.DateTimeField(null=True, blank=True)
    saldo_transaccion = models.FloatField(null=True, blank=True)
    decision_vendedor = models.BooleanField(default=False)

    def __str__(self):
        return f'Compra {self.id} - {self.usuario.username} - {self.fecha_compra}'

class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.IntegerField()

    def __str__(self):
        return f'{self.producto.nombre} x {self.cantidad}'

class InformacionPago(models.Model):
    usuario = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='informacion_pago')
    alias = models.CharField(max_length=50, null=True, blank=True)
    numero_tarjeta = models.CharField(max_length=20, blank=True, null=True)
    tipo_tarjeta = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        abstract = True

class TarjetaCredito(InformacionPago):
    activa = models.BooleanField(default=True)

    def __str__(self):
        return f'Tarjeta {self.tipo_tarjeta} - {self.numero_tarjeta[-4:]}'

# Nuevos modelos para el carrito
class Carrito(models.Model):
    usuario = models.OneToOneField(Cliente, on_delete=models.CASCADE, related_name='carrito')

class ItemCarrito(models.Model):
    carrito = models.ForeignKey(Carrito, on_delete=models.CASCADE, related_name='items')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)