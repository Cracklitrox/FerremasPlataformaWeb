from django import forms
from .models import Administrador
from django.contrib.auth.models import Group

class AdministradorCreacionForm(forms.ModelForm):
    class Meta:
        model = Administrador
        fields = ('primer_nombre', 'primer_apellido', 'correo', 'run', 'dv_run')

    def save(self, commit=True):
        administrador = super().save(commit=False)
        administrador.username = f"{self.cleaned_data['primer_nombre']}_{self.cleaned_data['primer_apellido']}"
        # Generar la contraseña
        password = (f"{self.cleaned_data['primer_nombre'][:3]}{self.cleaned_data['primer_apellido'][:3]}_{self.cleaned_data['run']}")
        administrador.password = password
        if commit:
            administrador.save()
            grupo, created = Group.objects.get_or_create(name='Administrador')
            administrador.groups.add(grupo)
            administrador.save()
        return administrador