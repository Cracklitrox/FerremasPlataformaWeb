import os
import django
from django.core.management import call_command

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ferremas_market.settings')
django.setup()

with open('productos_categoria.json', 'r', encoding='utf-8') as archivo:
    call_command('loaddata', 'productos.json')