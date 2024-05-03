from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

# Create your models here.

class UsuarioManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('El nombre de usuario debe ser rellenado.')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('El campo "is_staff" debe esta activo')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('El campo "is_superuser"" debe estar activo')

        return self.create_user(username, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    run = models.IntegerField(8, unique=True)
    dv_run = models.CharField(1)
    primer_nombre = models.CharField(max_length=30)
    primer_apellido = models.CharField(max_length=45)
    numero_telefonico = models.CharField(max_length=12)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=20, unique=True)
    correo = models.EmailField(max_length=70)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['run', 'correo']

    def __str__(self):
        return self.username


class Administrador(Usuario):
    debe_cambiar_password = models.BooleanField(default=True)

# Vendedor
class Vendedor(Usuario):
    area_de_venta = models.CharField(max_length=100, null=True, blank=True)

# Contador
class Contador(Usuario):
    nivel_de_acceso = models.IntegerField(default=1)

# Bodeguero
class Bodeguero(Usuario):
    almacen_asignado = models.CharField(max_length=100, null=True, blank=True)