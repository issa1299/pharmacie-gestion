from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from .models import Vente, LigneVente
from medicaments.models import Medicament
from clients.models import Client
from parametres.models import Parametres

def generer_numero_facture():
    annee = timezone.now().year
    count = Vente.objects.filter(date_vente__year=annee).count() + 1
    return f"FACT-{annee}-{count:04d}"

@login_required
def liste_ventes(request):
    ventes = Vente.objects.select_related('client', 'utilisateur').all()
    q = request.GET.get('q', '')
    if q:
        ventes = ventes.filter(
            Q(numero_facture__icontains=q) |
            Q(client__nom__icontains=q) |
            Q(client__prenom__icontains=q)
        )
    return render(request, 'ventes/liste.html', {
        'ventes': ventes,
        'q': q,
    })

@login_required
def nouvelle_vente(request):
    medicaments = Medicament.objects.filter(quantite_stock__gt=0)
    clients = Client.objects.all()

    if request.method == 'POST':
        client_id = request.POST.get('client')
        medicament_ids = request.POST.getlist('medicament_id')
        quantites = request.POST.getlist('quantite')

        if not medicament_ids:
            messages.error(request, "Ajoutez au moins un médicament !")
            return render(request, 'ventes/nouvelle.html', {
                'medicaments': medicaments, 'clients': clients
            })

        # Créer la vente
        vente = Vente.objects.create(
            client_id=client_id if client_id else None,
            utilisateur=request.user,
            numero_facture=generer_numero_facture(),
            total=0
        )

        total = 0
        for med_id, qte in zip(medicament_ids, quantites):
            qte = int(qte)
            med = Medicament.objects.get(pk=med_id)
            if qte > med.quantite_stock:
                messages.error(request, f"Stock insuffisant pour {med.nom} !")
                vente.delete()
                return render(request, 'ventes/nouvelle.html', {
                    'medicaments': medicaments, 'clients': clients
                })
            LigneVente.objects.create(
                vente=vente,
                medicament=med,
                quantite=qte,
                prix_unitaire=med.prix_vente,
                sous_total=qte * med.prix_vente
            )
            # Déduire du stock
            med.quantite_stock -= qte
            med.save()
            total += qte * med.prix_vente

        vente.total = total
        vente.save()
        messages.success(request, f"Vente {vente.numero_facture} enregistrée !")
        return redirect('ventes:detail', pk=vente.pk)

    return render(request, 'ventes/nouvelle.html', {
        'medicaments': medicaments,
        'clients': clients,
    })

@login_required
def detail_vente(request, pk):
    vente = get_object_or_404(Vente, pk=pk)
    lignes = vente.lignes.select_related('medicament').all()
    params, _ = Parametres.objects.get_or_create(pk=1)
    return render(request, 'ventes/detail.html', {
        'vente': vente,
        'lignes': lignes,
        'site_params': params,
        'params': params,
    })
