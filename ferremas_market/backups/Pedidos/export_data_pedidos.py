import os
import sys
import django
from django.core.management import call_command

# Configurar el entorno de Django
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(project_path)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ferremas_market.settings')
django.setup()

backup_dir = os.path.join(project_path, 'backups_archivo')
os.makedirs(backup_dir, exist_ok=True)
backup_file = os.path.join(backup_dir, 'productos_categoria.json')

with open(backup_file, 'w', encoding='utf-8') as archivo:
    call_command('dumpdata', 
                 'Pedidos.Categoria', 
                 'Pedidos.Producto', 
                 indent=2, 
                 use_natural_foreign_keys=True, 
                 stdout=archivo)