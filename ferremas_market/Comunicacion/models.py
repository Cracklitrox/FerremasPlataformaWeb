from django.db import models
from Usuario.models import Cliente

# Create your models here.

class TipoComunicacion(models.Model):
    descripcion = models.CharField(max_length=120)
    foto = models.ImageField(upload_to='tipo_comunicacion/%Y/%m/%d/', blank=True)

class Suscripcion(models.Model):
    cliente = models.OneToOneField(
        Cliente,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='suscripcion'
    )
    tipo_comunicacion = models.ForeignKey(
        TipoComunicacion,
        on_delete=models.CASCADE,
        related_name='suscripciones'
    )
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.cliente.run} -> {self.tipo_comunicacion.descripcion}"