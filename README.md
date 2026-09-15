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

> ⚠️ Aucun mot de passe par défaut en production. Créez toujours votre super-utilisateur :
> ```bash
> python manage.py createsuperuser
> ```

DÉPLOIEMENT SUR PYTHONANYWHERE
==============================

Le projet est prêt pour PythonAnywhere (sur ce plan on garde SQLite :
vos données locales sont conservées telles quelles, pas besoin de PostgreSQL).

Remplacer dans ces étapes ``MONUTILISATEUR`` par votre nom d'utilisateur
PythonAnywhere (ex. ``issa``) et ``pharmagest`` par votre mot de passe.

1. Créez un compte gratuit sur https://www.pythonanywhere.com
2. Onglet **Consoles** → **Bash** (nouvelle console), puis :
   ```bash
   # Récupérer le code
   git clone https://github.com/issa1299/pharmacie-gestion.git
   cd pharmacie-gestion/pharmacie_project

   # Environnement virtuel + dépendances
   mkvirtualenv --python=/usr/bin/python3.12 pharmagest
   pip install -r requirements.txt
   ```
   (Si ``python3.12`` n'existe pas, essayez ``python3.13`` ou ``python3.11``.)
3. Fichiers de configuration (dans ``~/pharmacie-gestion/pharmacie_project/``) :
   ```bash
   cp .env.example .env
   nano .env    # mettre DEBUG=False, SECRET_KEY (une longue clé aléatoire),
                # PYTHONANYWHERE_HOST=MONUTILISATEUR.pythonanywhere.com
   ```
4. Base de données + admin + fichiers statiques :
   ```bash
   python manage.py migrate
   python manage.py createsuperuser   # crée l'admin (nom + mot de passe)
   python manage.py collectstatic --noinput
   ```
   💡 Pour récupérer VOS données actuelles : onglet **Files** → naviguez vers
   ``/home/MONUTILISATEUR/`` → téléversez votre ``db.sqlite3`` local à la place
   de celui créé (ensuite pas besoin de ``migrate``/``createsuperuser``).
5. Onglet **Web** → **Add a new web app** :
   - « Manual configuration » → choisissez la même version Python que le venv.
   - « Source code » → ``/home/MONUTILISATEUR/pharmacie-gestion/pharmacie_project``
   - « Working directory » → ``/home/MONUTILISATEUR/``
   - « Virtualenv » → ``/home/MONUTILISATEUR/.virtualenvs/pharmagest``
6. Cliquez sur le lien **WSGI configuration file** et mettez tout le contenu :
   💡 Le fichier prêt à l'emploi est dans le dépôt :
   ``pythonanywhere_wsgi.example.py`` (racine du dépôt) — ouvrez-le dans
   l'onglet **Files** de PythonAnywhere, copiez tout son contenu sans espaces,
   et collez-le dans l'éditeur WSGI :
   ```python
   import os
   import sys
   from dotenv import load_dotenv

   PROJECT = '/home/MONUTILISATEUR/pharmacie-gestion/pharmacie_project'
   if PROJECT not in sys.path:
       sys.path.append(PROJECT)

   load_dotenv(os.path.join(PROJECT, '.env'))

   os.environ['DJANGO_SETTINGS_MODULE'] = 'pharmacie_project.settings'

   from django.core.wsgi import get_wsgi_application
   application = get_wsgi_application()
   ```
7. Section **Static files** (deux lignes à ajouter) :
   - URL `/static/` → `/home/MONUTILISATEUR/pharmacie-gestion/pharmacie_project/staticfiles/`
   - URL `/media/` → `/home/MONUTILISATEUR/pharmacie-gestion/pharmacie_project/media/`
8. Cliquez sur le bouton vert **Reload** en haut de la page **Web**.
9. Votre site est en ligne : ``https://MONUTILISATEUR.pythonanywhere.com``
10. À chaque mise à jour du code :
    ```bash
    git pull
    pip install -r requirements.txt   # si les deps changent
    python manage.py migrate          # si des migrations changent
    python manage.py collectstatic --noinput
    ```
    puis **Reload** dans l'onglet Web.

Variables optionnelles (dans le fichier ``.env``) :
- Email SMTP : ``EMAIL_HOST``, ``EMAIL_PORT``, ``EMAIL_HOST_USER``,
  ``EMAIL_HOST_PASSWORD``, ``DEFAULT_FROM_EMAIL``
- SMS Twilio : ``TWILIO_ACCOUNT_SID``, ``TWILIO_AUTH_TOKEN``, ``TWILIO_FROM_NUMBER``

> Remarque sécurité : la réinitialisation directe de mot de passe
> (``/gestion/reset-password/``) est désactivée en production (réservée au
> développement). En production, utilisez le flux « mot de passe oublié ».

> Le déploiement Render (``render.yaml`` + gunicorn) reste disponible mais n'est
> plus la voie recommandée.

SÉCURITÉ
========

Mesures actives en production :
- ``DEBUG=False`` et ``SECRET_KEY`` dans le fichier ``.env`` (jamais commité).
- ``ALLOWED_HOSTS`` restreint au domaine réel (``PYTHONANYWHERE_HOST``).
- Réinitialisation directe de mot de passe (``/gestion/reset-password/``)
  **désactivée en production**.
- Anti force brute : 5 échecs de connexion → blocage 5 minutes
  (``ACCOUNT_RATE_LIMITS['login_failed'] = '5/5m/key'``).
- HTTPS uniquement : ``SECURE_SSL_REDIRECT=True``, ``SESSION_COOKIE_SECURE=True``,
  ``CSRF_COOKIE_SECURE=True`` dans le ``.env``.
- Mots de passe hachés (pbkdf2/sha256), ``X-Frame-Options: DENY``.

Bonnes pratiques :
- Gardez le ``.env`` secret et utilisez un mot de passe admin fort.
- Sauvegardez régulièrement ``db.sqlite3`` (onglet Files → télécharger).
- Configurez un vrai serveur SMTP pour que les codes « mot de passe oublié »
  partent par email (sinon ils apparaissent dans les logs).

Sauvegarde automatique recommandée
----------------------------------
Une commande intégrée crée une sauvegarde JSON complète de la base dans
``backups/`` et ne conserve que les 7 dernières (rotation automatique) :

.. code-block:: bash

    python manage.py sauvegarde_bd          # à la main
    python manage.py sauvegarde_bd --garder 14   # garder 14 sauvegardes

Pour la rendre quotidienne sur PythonAnywhere : onglet **Tasks** →
**Create a new task**, horaire voulu (ex. ``3:30``), commande :

::

    workon pharmagest && cd ~/pharmacie-gestion/pharmacie_project && python manage.py sauvegarde_bd

Pour restaurer une sauvegarde (attention : remplace les données actuelles) :

.. code-block:: bash

    python manage.py flush --noinput
    python manage.py loaddata backups/sauvegarde_AAAAMMJJ_HHMM.json

Exports CSV
-----------
Boutons « CSV » dans les listes **ventes**, **médicaments**, **clients** et
**mouvements de stock** : téléchargent un fichier lisible directement dans
Excel (séparateur ``;``). Les rapports suivent les filtres actifs là où
appliqué (ventes : recherche + statut).

Caisse Express
--------------
La page « Nouvelle vente » est une caisse optimisée pour les caissiers :
recherche instantanée, filtres par catégorie, **scan code-barres** (le champ
scan lit, ajoute au ticket et re-arme automatiquement), clavier tactile pour
les quantités, calcul du **monnaie à rendre**, raccourcis clavier (F1 focus
recherche, F4 vider le ticket, F9 valider/Enregistrer, Échap fermer le
clavier) et choix du client + mode de paiement sur un seul écran.

