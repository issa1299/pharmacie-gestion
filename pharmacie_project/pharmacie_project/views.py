# pharmacie_project/views.py
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import DecimalField, F, Sum, Value, Q
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from decimal import Decimal
from medicaments.models import Medicament
from ventes.models import Vente


@login_required
def dashboard(request):
    aujourd_hui = timezone.localdate()
    ventes_du_jour = Vente.objects.filter(
        date_vente__date=aujourd_hui,
        statut='validee',
    ).select_related('client', 'utilisateur')
    medicaments_stock_faible = Medicament.objects.filter(
        quantite_stock__lte=F('seuil_alerte')
    ).select_related('categorie')

    return render(request, 'dashboard.html', {
        'total_medicaments': Medicament.objects.count(),
        'ventes_jour': ventes_du_jour.count(),
        'stock_faible': medicaments_stock_faible.count(),
        'ca_jour': ventes_du_jour.aggregate(
            total=Coalesce(
                Sum('total'),
                Value(Decimal('0.00')),
                output_field=DecimalField(max_digits=10, decimal_places=2),
            )
        )['total'],
        'dernieres_ventes': ventes_du_jour[:8],
        'medicaments_stock_faible': medicaments_stock_faible,
        'medicaments_expires': Medicament.objects.filter(
            date_expiration__isnull=False,
            date_expiration__lte=aujourd_hui,
        ),
    })


@login_required
def recherche_globale(request):
    """API de recherche rapide — médicaments, factures, clients.

    Utilisée par la barre de recherche du tableau de bord (autocomplete).
    Renvoie du JSON : [{type, label, detail, url}, ...]
    """
    q = (request.GET.get('q') or '').strip()
    if len(q) < 2:
        return JsonResponse({'results': []})

    resultats = []

    # ── Médicaments (max 5) ──
    for med in Medicament.objects.filter(
        Q(nom__icontains=q) | Q(code_barre__icontains=q)
    ).select_related('categorie')[:5]:
        statut = '⚠️ Stock faible' if med.quantite_stock <= med.seuil_alerte else f'Stock : {med.quantite_stock}'
        resultats.append({
            'type': 'medicament',
            'icone': 'capsule-pill',
            'label': med.nom,
            'detail': f"{med.prix_vente} FCFA · {statut}",
            'url': f"/medicaments/?q={q}",
        })

    # ── Factures / ventes (max 4) ──
    for vente in Vente.objects.filter(
        numero_facture__icontains=q
    ).select_related('client')[:4]:
        client = str(vente.client) if vente.client else 'Client anonyme'
        resultats.append({
            'type': 'vente',
            'icone': 'receipt',
            'label': vente.numero_facture,
            'detail': f"{client} · {vente.total} FCFA",
            'url': f"/ventes/{vente.pk}/",
        })

    # ── Clients (max 3) ──
    from clients.models import Client
    for client in Client.objects.filter(
        Q(nom__icontains=q) | Q(prenom__icontains=q) | Q(telephone__icontains=q)
    )[:3]:
        resultats.append({
            'type': 'client',
            'icone': 'person',
            'label': str(client),
            'detail': client.telephone or 'Sans téléphone',
            'url': f"/clients/{client.pk}/",
        })

    return JsonResponse({'results': resultats})


@login_required
def relancer_paiement(request, pk):
    """Relance une vente bloquée en 'en_attente' : régénère le lien de
    paiement (nouveau secret + référence) ou l'annule si le stock a fondu."""
    from ventes.services.payment import initier_paiement
    vente = get_object_or_404(Vente, pk=pk)
    if vente.statut_paiement != 'en_attente':
        messages.info(request, "Cette vente n'est plus en attente de paiement.")
        return redirect('ventes:detail', pk=vente.pk)
    # Vérifier que le stock est toujours disponible avant de relancer
    for ligne in vente.lignes.select_related('medicament').all():
        med = Medicament.objects.filter(pk=ligne.medicament_id).first()
        if not med or ligne.quantite > med.quantite_stock:
            messages.error(
                request,
                f"Stock insuffisant pour relancer ({ligne.medicament.nom}) — "
                "annulez plutôt la vente."
            )
            return redirect('ventes:detail', pk=vente.pk)
    with transaction.atomic():
        url_paiement = initier_paiement(vente)
    messages.info(request, "Nouveau lien de paiement généré.")
    return redirect(url_paiement)

