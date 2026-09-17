"""
Commande pour peupler la base avec des catégories et médicaments de base.

    python manage.py seed_medicaments
"""

from django.core.management.base import BaseCommand
from medicaments.models import Categorie, Etagere, Medicament


CATEGORIES = [
    ('Antalgiques', 'Médicaments contre la douleur'),
    ('Antibiotiques', 'Médicaments antibactériens'),
    ('Anti-inflammatoires', 'Médicaments anti-inflammatoires'),
    ('Antipaludiques', 'Médicaments contre le paludisme'),
    ('Antipyrétiques', 'Médicaments contre la fièvre'),
    ('Vitamines et compléments', 'Compléments alimentaires et vitamines'),
    ('Dermatologie', 'Soins de la peau'),
    ('Gastro-entérologie', 'Médicaments du système digestif'),
    ('Respiratoire', 'Médicaments des voies respiratoires'),
    ('Cardiovasculaire', 'Médicaments du système cardiovasculaire'),
    ('Ophtalmologie', 'Soins des yeux'),
    ('ORL', 'Médicaments ORL'),
    ('Gynécologie', 'Médicaments gynécologiques'),
    ('Pédiatrie', 'Médicaments pour enfants'),
    ('Autres', 'Autres médicaments'),
]

ETAGERES = [
    ('ETG-A', 'Étagère A', '#0F6E56', 'bi-capsule', 'Rayon principal'),
    ('ETG-B', 'Étagère B', '#1A73E8', 'bi-capsule', 'Rayon secondaire'),
    ('ETG-C', 'Étagère C', '#E8710A', 'bi-capsule', 'Réserve'),
    ('ETG-D', 'Étagère D', '#C62828', 'bi-capsule', 'Vitrine'),
]

MEDICAMENTS = [
    # Antalgiques
    {'nom': 'Paracétamol 500mg', 'categorie': 'Antalgiques', 'prix_achat': 100, 'prix_vente': 250, 'stock': 50, 'seuil': 10, 'description': 'Antalgique antipyrétique'},
    {'nom': 'Paracétamol 1g', 'categorie': 'Antalgiques', 'prix_achat': 150, 'prix_vente': 350, 'stock': 30, 'seuil': 8, 'description': 'Antalgique antipyrétique dosage fort'},
    {'nom': 'Ibuprofène 400mg', 'categorie': 'Anti-inflammatoires', 'prix_achat': 120, 'prix_vente': 300, 'stock': 25, 'seuil': 8, 'description': 'Anti-inflammatoire non stéroïdien'},
    {'nom': 'Aspirine 500mg', 'categorie': 'Antalgiques', 'prix_achat': 80, 'prix_vente': 200, 'stock': 40, 'seuil': 10, 'description': 'Antalgique antipyrétique antiagrégant'},
    {'nom': 'Doliprane 1000mg', 'categorie': 'Antalgiques', 'prix_achat': 200, 'prix_vente': 500, 'stock': 20, 'seuil': 5, 'description': 'Paracétamol 1g - Marque'},
    {'nom': 'Efferalgan 500mg', 'categorie': 'Antalgiques', 'prix_achat': 180, 'prix_vente': 450, 'stock': 15, 'seuil': 5, 'description': 'Paracétamol effervescent'},
    {'nom': 'Advil 200mg', 'categorie': 'Anti-inflammatoires', 'prix_achat': 250, 'prix_vente': 600, 'stock': 12, 'seuil': 4, 'description': 'Ibuprofène - Marque'},
    # Antibiotiques
    {'nom': 'Amoxicilline 1g', 'categorie': 'Antibiotiques', 'prix_achat': 300, 'prix_vente': 700, 'stock': 20, 'seuil': 5, 'description': 'Antibiotique pénicilline'},
    {'nom': 'Azithromicine 500mg', 'categorie': 'Antibiotiques', 'prix_achat': 500, 'prix_vente': 1200, 'stock': 15, 'seuil': 4, 'description': 'Antibiotique macrolide'},
    {'nom': 'Ciprofloxacine 500mg', 'categorie': 'Antibiotiques', 'prix_achat': 400, 'prix_vente': 900, 'stock': 18, 'seuil': 5, 'description': 'Antibiotique fluoroquinolone'},
    {'nom': 'Métronidazole 500mg', 'categorie': 'Antibiotiques', 'prix_achat': 150, 'prix_vente': 400, 'stock': 22, 'seuil': 6, 'description': 'Antibiotique antiparasitaire'},
    {'nom': 'Augmentin 1g', 'categorie': 'Antibiotiques', 'prix_achat': 600, 'prix_vente': 1500, 'stock': 10, 'seuil': 3, 'description': 'Amoxicilline + acide clavulanique'},
    # Antipaludiques
    {'nom': 'Coartem 20/120', 'categorie': 'Antipaludiques', 'prix_achat': 200, 'prix_vente': 500, 'stock': 30, 'seuil': 10, 'description': 'Arthéméter/Luméfantrine - Traitement paludisme'},
    {'nom': 'Nivaquine 100mg', 'categorie': 'Antipaludiques', 'prix_achat': 100, 'prix_vente': 250, 'stock': 25, 'seuil': 8, 'description': 'Chloroquine - Prophylaxie'},
    {'nom': 'Fansidar', 'categorie': 'Antipaludiques', 'prix_achat': 300, 'prix_vente': 750, 'stock': 15, 'seuil': 5, 'description': 'Sulfadoxine + Pyriméthamine'},
    {'nom': 'Malarone', 'categorie': 'Antipaludiques', 'prix_achat': 800, 'prix_vente': 2000, 'stock': 8, 'seuil': 3, 'description': 'Atovaquone/Proguanil - Prophylaxie'},
    # Antipyrétiques
    {'nom': 'Nurofen 200mg', 'categorie': 'Anti-inflammatoires', 'prix_achat': 200, 'prix_vente': 500, 'stock': 18, 'seuil': 5, 'description': 'Ibuprofène - Marque'},
    {'nom': 'Diclac 50mg', 'categorie': 'Anti-inflammatoires', 'prix_achat': 250, 'prix_vente': 600, 'stock': 12, 'seuil': 4, 'description': 'Diclofénac'},
    # Vitamines
    {'nom': 'Vitamine C 1g', 'categorie': 'Vitamines et compléments', 'prix_achat': 150, 'prix_vente': 400, 'stock': 35, 'seuil': 10, 'description': 'Complément vitamine C'},
    {'nom': 'Supradyn', 'categorie': 'Vitamines et compléments', 'prix_achat': 300, 'prix_vente': 700, 'stock': 20, 'seuil': 5, 'description': 'Multivitamines'},
    {'nom': 'Fer + Acide folique', 'categorie': 'Vitamines et compléments', 'prix_achat': 200, 'prix_vente': 500, 'stock': 25, 'seuil': 8, 'description': 'Complément en fer'},
    {'nom': 'Omnibionta', 'categorie': 'Vitamines et compléments', 'prix_achat': 400, 'prix_vente': 900, 'stock': 15, 'seuil': 4, 'description': 'Multivitamines + Minéraux'},
    # Dermatologie
    {'nom': 'Biafine 93g', 'categorie': 'Dermatologie', 'prix_achat': 500, 'prix_vente': 1200, 'stock': 10, 'seuil': 3, 'description': 'Émulsion cicatrisante'},
    {'nom': 'Fucidine 2%', 'categorie': 'Dermatologie', 'prix_achat': 600, 'prix_vente': 1400, 'stock': 8, 'seuil': 3, 'description': 'Crème antibactérienne'},
    {'nom': 'Dercutene', 'categorie': 'Dermatologie', 'prix_achat': 350, 'prix_vente': 800, 'stock': 12, 'seuil': 4, 'description': 'Crème solaire'},
    # Gastro
    {'nom': 'Smecta', 'categorie': 'Gastro-entérologie', 'prix_achat': 200, 'prix_vente': 500, 'stock': 20, 'seuil': 6, 'description': 'Anti-diarrhéique'},
    {'nom': 'Imodium', 'categorie': 'Gastro-entérologie', 'prix_achat': 300, 'prix_vente': 700, 'stock': 15, 'seuil': 5, 'description': 'Lopéramide - Anti-diarrhéique'},
    {'nom': 'Gaviscon', 'categorie': 'Gastro-entérologie', 'prix_achat': 250, 'prix_vente': 600, 'stock': 18, 'seuil': 5, 'description': 'Anti-acide gastro'},
    {'nom': 'Maalox', 'categorie': 'Gastro-entérologie', 'prix_achat': 200, 'prix_vente': 450, 'stock': 22, 'seuil': 6, 'description': 'Anti-acide'},
    # Respiratoire
    {'nom': 'Ventoline 100µg', 'categorie': 'Respiratoire', 'prix_achat': 800, 'prix_vente': 1800, 'stock': 10, 'seuil': 3, 'description': 'Bronchodilatateur'},
    {'nom': 'Ambrosol 30mg', 'categorie': 'Respiratoire', 'prix_achat': 200, 'prix_vente': 500, 'stock': 15, 'seuil': 5, 'description': 'Mucolytique'},
    {'nom': 'Darcohol', 'categorie': 'Respiratoire', 'prix_achat': 150, 'prix_vente': 350, 'stock': 20, 'seuil': 6, 'description': 'Sirop antitussif'},
    # Cardiovasculaire
    {'nom': 'Kardégic 75mg', 'categorie': 'Cardiovasculaire', 'prix_achat': 300, 'prix_vente': 700, 'stock': 15, 'seuil': 5, 'description': 'Antiagrégant plaquettaire'},
    {'nom': 'Amlodipine 5mg', 'categorie': 'Cardiovasculaire', 'prix_achat': 250, 'prix_vente': 600, 'stock': 12, 'seuil': 4, 'description': 'Antihypertenseur'},
    # ORL
    {'nom': 'Otriven 0.05%', 'categorie': 'ORL', 'prix_achat': 200, 'prix_vente': 450, 'stock': 18, 'seuil': 5, 'description': 'Spray nasal décongestionnant'},
    {'nom': 'Otolyse', 'categorie': 'ORL', 'prix_achat': 250, 'prix_vente': 550, 'stock': 12, 'seuil': 4, 'description': 'Gouttes auriculaires'},
    # Pédiatrie
    {'nom': 'Doliprane Enfant 2.4%', 'categorie': 'Pédiatrie', 'prix_achat': 300, 'prix_vente': 700, 'stock': 15, 'seuil': 5, 'description': 'Paracétamol pédiatrique sirop'},
    {'nom': 'Nurofen Enfant', 'categorie': 'Pédiatrie', 'prix_achat': 350, 'prix_vente': 800, 'stock': 12, 'seuil': 4, 'description': 'Ibuprofène pédiatrique'},
    {'nom': 'Spasfon Enfant', 'categorie': 'Pédiatrie', 'prix_achat': 200, 'prix_vente': 500, 'stock': 10, 'seuil': 3, 'description': 'Antispasmodique pédiatrique'},
]


class Command(BaseCommand):
    help = 'Peuple la base avec des catégories, étagères et médicaments de base'

    def handle(self, *args, **options):
        # Catégories
        cats_created = 0
        for nom, desc in CATEGORIES:
            _, created = Categorie.objects.get_or_create(nom=nom, defaults={'description': desc})
            if created:
                cats_created += 1
        self.stdout.write(self.style.SUCCESS(f'{cats_created} catégorie(s) créée(s)'))

        # Étagères
        etg_created = 0
        for code, nom, couleur, icone, emplacement in ETAGERES:
            _, created = Etagere.objects.get_or_create(
                code=code,
                defaults={'nom': nom, 'couleur': couleur, 'icone': icone, 'emplacement': emplacement},
            )
            if created:
                etg_created += 1
        self.stdout.write(self.style.SUCCESS(f'{etg_created} étagère(s) créée(s)'))

        # Médicaments
        cats_map = {c.nom: c for c in Categorie.objects.all()}
        etgs = list(Etagere.objects.all())
        meds_created = 0
        for i, m in enumerate(MEDICAMENTS):
            if Medicament.objects.filter(nom=m['nom']).exists():
                continue
            cat = cats_map.get(m['categorie'])
            etg = etgs[i % len(etgs)] if etgs else None
            prix_achat = m.get('prix_achat', m.get('prix_achat', 0))
            Medicament.objects.create(
                nom=m['nom'],
                categorie=cat,
                etagere=etg,
                description=m.get('description', ''),
                prix_achat=prix_achat,
                prix_vente=m['prix_vente'],
                quantite_stock=m['stock'],
                seuil_alerte=m['seuil'],
                code_barre='',
            )
            meds_created += 1
        self.stdout.write(self.style.SUCCESS(f'{meds_created} médicament(s) créé(s)'))
