from django import forms
from .models import Administrador, Bodeguero
from django.contrib.auth.hashers import make_password

class AdministradorCreacionForm(forms.ModelForm):
    class Meta:
        model = Administrador
        fields = ('primer_nombre', 'primer_apellido', 'correo', 'run', 'dv_run')

    def save(self, commit=True):
        administrador = super().save(commit=False)
        administrador.username = f"{self.cleaned_data['primer_nombre']}_{self.cleaned_data['primer_apellido']}"
        # Generar la contraseña específica
        password = make_password(f"{self.cleaned_data['primer_nombre'][:3]}{self.cleaned_data['primer_apellido'][:3]}_{self.cleaned_data['run']}")
        administrador.set_password(password)
        if commit:
            administrador.save()
        return administrador