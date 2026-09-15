"""Export CSV des listes — ouvrables directement dans Excel."""
import csv
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse

from .models import Vente
from medicaments.models import Medicament
from clients.models import Client
from stock.models import MouvementStock


def _reponse_csv(nom_fichier):
    resp = HttpResponse(content_type='text/csv; charset=utf-8')
    resp['Content-Disposition'] = f'attachment; filename="{nom_fichier}"'
    return resp


@login_required
def export_ventes_csv(request):
    """Export des ventes (1 ligne par vente, avec client et caissier)."""
    resp = _reponse_csv('ventes.csv')
    writer = csv.writer(resp, delimiter=';')
    writer.writerow([
        'N° Facture', 'Date', 'Client', 'Caissier', 'Articles',
        'Total', 'Remise', 'Net à payer', 'Mode paiement',
        'Statut paiement', 'Statut',
    ])
    ventes = Vente.objects.select_related('client', 'utilisateur').order_by('-date_vente')
    for v in ventes:
        nb_articles = sum(l.quantite for l in v.lignes.all())
        writer.writerow([
            v.numero_facture,
            v.date_vente.strftime('%d/%m/%Y %H:%M'),
            str(v.client) if v.client else '—',
            v.utilisateur.get_full_name() or v.utilisateur.username if v.utilisateur else '—',
            nb_articles,
            v.total, v.remise, v.net_a_payer,
            v.get_mode_paiement_display(),
            v.get_statut_paiement_display(),
            v.get_statut_display(),
        ])
    return resp


@login_required
def export_vente_detail_csv(request, pk):
    """Export du détail d'une vente (1 ligne par médicament vendu)."""
    vente = Vente.objects.get(pk=pk)
    resp = _reponse_csv(f'{vente.numero_facture}.csv')
    writer = csv.writer(resp, delimiter=';')
    writer.writerow([
        'N° Facture', 'Date', 'Médicament', 'Code-barres',
        'Quantité', 'Prix unitaire', 'Sous-total',
    ])
    for l in vente.lignes.select_related('medicament').all():
        writer.writerow([
            vente.numero_facture,
            vente.date_vente.strftime('%d/%m/%Y %H:%M'),
            l.medicament.nom,
            l.medicament.code_barre or '—',
            l.quantite, l.prix_unitaire, l.sous_total,
        ])
    return resp


@login_required
def export_medicaments_csv(request):
    """Export du catalogue complet, y compris stock à zéro."""
    resp = _reponse_csv('medicaments.csv')
    writer = csv.writer(resp, delimiter=';')
    writer.writerow([
        'Nom', 'Catégorie', 'Code-barres', 'Prix achat', 'Prix vente',
        'Stock', 'Seuil alerte', 'Étagère', 'Date expiration',
    ])
    meds = (
        Medicament.objects.select_related('categorie', 'etagere')
        .order_by('nom')
    )
    for m in meds:
        writer.writerow([
            m.nom,
            m.categorie.nom if m.categorie else '—',
            m.code_barre or '—',
            m.prix_achat, m.prix_vente, m.quantite_stock,
            getattr(m, 'seuil_alerte', '—'),
            m.etagere.nom if getattr(m, 'etagere', None) else '—',
            m.date_expiration.strftime('%d/%m/%Y') if getattr(m, 'date_expiration', None) else '—',
        ])
    return resp


@login_required
def export_clients_csv(request):
    """Export des clients avec statistiques d'achat (ventes validées)."""
    from django.db.models import Count, Q, Sum
    resp = _reponse_csv('clients.csv')
    writer = csv.writer(resp, delimiter=';')
    writer.writerow([
        'Nom', 'Prénom', 'Téléphone', 'Email', 'Adresse',
        'Nb achats', 'Total dépensé',
    ])
    ventes_validees = Q(ventes__statut='validee')
    clients = Client.objects.annotate(
        nb_ventes=Count('ventes', filter=ventes_validees),
        _total_brut=Sum('ventes__total', filter=ventes_validees),
        _total_remises=Sum('ventes__remise', filter=ventes_validees),
    ).order_by('nom')
    for c in clients:
        total = (c._total_brut or 0) - (c._total_remises or 0)
        writer.writerow([
            c.nom, c.prenom, c.telephone or '—', c.email or '—',
            c.adresse or '—', c.nb_ventes, total,
        ])
    return resp


@login_required
def export_mouvements_csv(request):
    """Export du journal de stock (entrées/sorties/ajustements)."""
    resp = _reponse_csv('mouvements_stock.csv')
    writer = csv.writer(resp, delimiter=';')
    writer.writerow([
        'Date', 'Médicament', 'Type', 'Quantité', 'Motif', 'Utilisateur',
    ])
    for m in (
        MouvementStock.objects.select_related('medicament', 'utilisateur')
        .order_by('-date')
    ):
        writer.writerow([
            m.date.strftime('%d/%m/%Y %H:%M'),
            m.medicament.nom,
            m.get_type_mouvement_display(),
            m.quantite, m.motif or '—',
            m.utilisateur.get_full_name() or m.utilisateur.username if m.utilisateur else '—',
        ])
    return resp
