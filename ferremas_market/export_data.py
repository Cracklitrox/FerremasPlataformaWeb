import os
import django
from django.core.management import call_command

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ferremas_market.settings')
django.setup()

with open('productos_categoria.json', 'w', encoding='utf-8') as archivo:
    call_command('dumpdata', 'Pedidos.Categoria', 'Pedidos.Producto', indent=2, use_natural_foreign_keys=True, stdout=archivo)