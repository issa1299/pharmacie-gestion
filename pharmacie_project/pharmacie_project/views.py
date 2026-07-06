# pharmacie_project/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.db.models import DecimalField, F, Sum, Value
from django.db.models.functions import Coalesce
from django.utils import timezone
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

