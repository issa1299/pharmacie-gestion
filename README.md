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

DÉPLOIEMENT SUR RENDER
======================

Le projet est prêt pour Render (blueprint ``render.yaml`` à la racine du dépôt).

1. Poussez le code sur GitHub :
   ```bash
   git add .
   git commit -m "Préparation déploiement Render"
   git push origin main
   ```
2. Dans Render Dashboard → **New** → **Blueprint**, choisissez le repo GitHub.
3. Render lit ``render.yaml`` et crée automatiquement :
   - le service web ``pharmagest`` (gunicorn + PostgreSQL),
   - la base PostgreSQL ``pharmagest-db`` (variable ``DATABASE_URL`` injectée),
   - `SECRET_KEY` générée, ``DEBUG=false``.
4. Le super-utilisateur est créé **automatiquement au build** (pas de Shell
   nécessaire sur le plan gratuit) :
   - À la création du Blueprint, Render vous demande de saisir le mot de passe
     de ``DJANGO_SUPERUSER_PASSWORD`` (username = ``admin``).
   - Ou ajoutez-le après coup dans **Dashboard → Environment** :
     ``DJANGO_SUPERUSER_PASSWORD=monMdpF0rt`` puis relancez un déploiement
     (bouton **Deploy** → **Clear build cache & deploy**).
   - Si ``DJANGO_SUPERUSER_PASSWORD`` reste vide, aucun admin n'est créé et le
     build affiche un message d'avertissement (visible dans les logs).
5. Ouvrez l'URL ``https://pharmagest.onrender.com`` et connectez-vous avec
   ``admin`` et le mot de passe choisi.

   > Remarque sécurité : le réinitialisation directe de mot de passe
   > (``/gestion/reset-password/``) est désactivée en production (réservée au
   > développement). En production, utilisez le flux « mot de passe oublié »
   > par email + code.

Variables optionnelles (Dashboard → Environment) :
- Email SMTP : ``EMAIL_HOST``, ``EMAIL_PORT``, ``EMAIL_HOST_USER``, ``EMAIL_HOST_PASSWORD``, ``DEFAULT_FROM_EMAIL``
- SMS Twilio : ``TWILIO_ACCOUNT_SID``, ``TWILIO_AUTH_TOKEN``, ``TWILIO_FROM_NUMBER``

⚠️ Attention : sur le plan gratuit Render, les fichiers médias (logos, photos) et
les bases SQLite sont éphémères. La base PostgreSQL persiste ; pour les uploads,
ajoutez un *Persistent Disk* (plan payant) monté sur ``/opt/render/project/media``.
