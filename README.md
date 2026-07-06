INSTALLATION PHARMAGEST
=======================

1. Installer Python 3.11+
2. Ouvrir le terminal dans le dossier pharmacie_project
3. Créer l'environnement virtuel :
   python -m venv env
4. Activer l'environnement :
   env\Scripts\activate
5. Installer les dépendances :
   pip install -r requirements.txt
6. Lancer les migrations :
   python manage.py migrate
7. Créer un compte admin :
   python manage.py createsuperuser
8. Lancer le serveur :
   python manage.py runserver
9. Ouvrir : http://127.0.0.1:8000

COMPTE DEMO : admin / admin123
