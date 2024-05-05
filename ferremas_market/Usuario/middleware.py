from django.shortcuts import redirect
from django.urls import reverse

class RequiereCambioDePasswordMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    # No cambios aun
    # Modificar ruta de cambio contraseña
    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated and hasattr(request.user, 'contrasena_cambiada'):
            if not request.user.contrasena_cambiada and not request.path.startswith(reverse('nombre_de_tu_url_para_cambio_de_contraseña')):
                return redirect('nombre_de_tu_url_para_cambio_de_contraseña')
        return response