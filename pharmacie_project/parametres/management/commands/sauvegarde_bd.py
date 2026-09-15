"""
Sauvegarde automatique de la base — à lancer en tâche planifiée PythonAnywhere :

    workon pharmagest
    cd ~/pharmacie-gestion/pharmacie_project
    python manage.py sauvegarde_bd

Crée backups/sauvegarde_AAAAMMJJ_HHMM.json (données complètes).
Ne conserve que les --garder plus récentes (7 par défaut).
"""
import os
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Sauvegarde la base dans backups/ (JSON) et supprime les plus anciennes."

    def add_arguments(self, parser):
        parser.add_argument(
            '--garder', type=int, default=7,
            help="Nombre de sauvegardes à conserver (défaut : 7).",
        )
        parser.add_argument(
            '--dossier', default=None,
            help="Dossier de destination (défaut : <projet>/backups).",
        )

    def handle(self, *args, **options):
        # sauvegarde_bd.py -> commands -> management -> parametres -> projet
        base_dir = Path(__file__).resolve().parents[3]  # pharmacie_project/
        dossier = Path(options['dossier']) if options['dossier'] else base_dir / 'backups'
        dossier.mkdir(parents=True, exist_ok=True)

        from django.utils import timezone
        stamp = timezone.localtime().strftime('%Y%m%d_%H%M')
        fichier = dossier / f'sauvegarde_{stamp}.json'

        # dumpdata exclusif : tables techniques inutiles à restaurer
        with open(fichier, 'w', encoding='utf-8') as f:
            call_command(
                'dumpdata',
                exclude=[
                    'contenttypes', 'auth.Permission', 'admin.logentry',
                    'sessions',
                ],
                indent=2, stdout=f,
            )

        taille_ko = fichier.stat().st_size / 1024
        self.stdout.write(self.style.SUCCESS(
            f"[OK] Sauvegarde creee : {fichier.name} ({taille_ko:.0f} Ko)"
        ))

        # Rotation : garder les N plus récentes
        garder = max(1, options['garder'])
        toutes = sorted(dossier.glob('sauvegarde_*.json'))
        for ancienne in toutes[:-garder]:
            ancienne.unlink()
            self.stdout.write(f"  - supprimee (ancienne) : {ancienne.name}")

        self.stdout.write(
            f"{len(toutes)} sauvegarde(s) au total, {garder} conservee(s)."
        )

