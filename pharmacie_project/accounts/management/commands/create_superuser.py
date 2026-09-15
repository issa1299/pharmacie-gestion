import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = (
        "Crée le super-utilisateur initial depuis les variables d'environnement "
        "DJANGO_SUPERUSER_USERNAME / DJANGO_SUPERUSER_EMAIL / DJANGO_SUPERUSER_PASSWORD. "
        "Idempotent : sans danger à chaque déploiement. "
        "Permet de créer l'admin Render sans accès Shell (plan gratuit)."
    )

    def handle(self, *args, **options):
        User = get_user_model()
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin").strip()
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@localhost").strip()
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "").strip()

        if not password:
            self.stdout.write(self.style.WARNING(
                "DJANGO_SUPERUSER_PASSWORD non définie "
                "— aucun super-utilisateur créé."
            ))
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING(
                f"Super-utilisateur '{username}' déjà présent — aucune action."
            ))
            return

        User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS(
            f"Super-utilisateur '{username}' créé avec succès."
        ))