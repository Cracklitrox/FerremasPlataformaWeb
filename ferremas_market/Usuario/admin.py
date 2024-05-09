from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Cliente, Administrador, Cliente, Vendedor, Bodeguero, Contador, Usuario
from .forms import AdministradorCreacionForm

class AdministradorAdmin(UserAdmin):
    add_form = AdministradorCreacionForm
    form = AdministradorCreacionForm
    model = Administrador
    fieldsets = (
        (None, {'fields': ('primer_nombre', 'primer_apellido', 'correo', 'run', 'dv_run', 'password', 'contrasena_cambiada')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('primer_nombre', 'primer_apellido', 'correo', 'run', 'dv_run'),
        }),
    )
    list_display = ('primer_nombre', 'primer_apellido', 'correo', 'run', 'dv_run')

admin.site.register(Administrador, AdministradorAdmin)
admin.site.register(Cliente)
admin.site.register(Vendedor)
admin.site.register(Bodeguero)
admin.site.register(Contador)
admin.site.register(Usuario)