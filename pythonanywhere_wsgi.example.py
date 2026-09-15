# ============================================================
# Fichier WSGI à coller dans PythonAnywhere :
#   Web tab -> WSGI configuration file  (/var/www/issa66_pythonanywhere_com_wsgi.py)
# ATTENTION : ne pas ajouter d'espace en début de ligne.
# ============================================================

import os
import sys
from dotenv import load_dotenv

PROJECT = '/home/issa66/pharmacie-gestion/pharmacie_project'
if PROJECT not in sys.path:
    sys.path.append(PROJECT)

load_dotenv(os.path.join(PROJECT, '.env'))

os.environ['DJANGO_SETTINGS_MODULE'] = 'pharmacie_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()