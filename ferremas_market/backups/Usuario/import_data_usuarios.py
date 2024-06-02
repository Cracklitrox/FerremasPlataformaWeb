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
backup_file = os.path.join(backup_dir, 'usuarios_backup.json')

with open(backup_file, 'r', encoding='utf-8') as archivo:
    call_command('loaddata', backup_file)