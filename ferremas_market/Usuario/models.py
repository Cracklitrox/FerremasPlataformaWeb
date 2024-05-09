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


class Usuario(AbstractBaseUser, PermissionsMixin):
    run = models.IntegerField(unique=True)
    dv_run = models.CharField(max_length=1)
    primer_nombre = models.CharField(max_length=30)
    primer_apellido = models.CharField(max_length=45)
    numero_telefonico = models.CharField(max_length=12)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=20)
    correo = models.EmailField(max_length=70)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['primer_nombre', 'primer_apellido', 'correo', 'run', 'dv_run']

    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='Grupos',
        blank=True,
        help_text='Los grupos a los que pertenece este usuario. Un usuario obtendrá todos los permisos concedidos a cada uno de sus grupos.',
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='Permisos de usuario',
        blank=True,
        help_text='Permisos específicos para este usuario.',
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
    )

    def __str__(self):
        return self.username


class Administrador(Usuario):
    contrasena_cambiada = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        self.is_staff = True
        self.is_superuser = False
        super().save(*args, **kwargs)

# Cliente
class Cliente(Usuario):
    pass

# Vendedor
class Vendedor(Usuario):
    pass

# Contador
class Contador(Usuario):
    pass

# Bodeguero
class Bodeguero(Usuario):
    pass