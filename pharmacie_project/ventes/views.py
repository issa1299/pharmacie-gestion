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
        
        mode_paiement = request.POST.get('mode_paiement', 'especes')
        try:
            remise = float(request.POST.get('remise', 0))
        except ValueError:
            remise = 0

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
            total=0,
            remise=remise,
            mode_paiement=mode_paiement,
            statut_paiement='paye' if mode_paiement == 'especes' else 'en_attente'
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
            # Déduire du stock UNIQUEMENT si c'est en espèces.
            # Pour l'API, on déduira lors de la réception du Webhook
            if mode_paiement == 'especes':
                med.quantite_stock -= qte
                med.save()
                
            total += qte * med.prix_vente

        vente.total = total
        vente.save()
        
        if mode_paiement != 'especes':
            from .services.payment import initier_paiement
            url_paiement = initier_paiement(vente)
            return redirect(url_paiement)
        else:
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

# ── PAIMENT API (MOCK) ────────────────────────────────────────────────────────

def mock_payment(request, pk):
    """
    Page fictive simulant l'interface de CinetPay / PaySika.
    L'utilisateur clique sur "Payer" et on déclenche le webhook.
    """
    vente = get_object_or_404(Vente, pk=pk)
    ref = request.GET.get('ref')
    
    if request.method == 'POST':
        # On simule le webhook envoyé par l'agrégateur en arrière-plan
        import requests
        from django.urls import reverse
        webhook_url = request.build_absolute_uri(reverse('ventes:webhook'))
        # Appel asynchrone / background normalement, mais ici on le fait en synchrone pour tester
        try:
            requests.post(webhook_url, json={'transaction_id': ref, 'status': 'ACCEPTED'})
        except:
            pass # Ignorer les erreurs réseau locales
            
        messages.success(request, "Paiement réussi via l'API !")
        return redirect('ventes:detail', pk=vente.pk)
        
    return render(request, 'ventes/mock_payment.html', {'vente': vente, 'ref': ref})


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def webhook_paiement(request):
    """
    URL appelée par l'agrégateur (CinetPay, etc.) quand un paiement aboutit.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            transaction_id = data.get('transaction_id')
            status = data.get('status')
            
            # Chercher la vente correspondante
            vente = Vente.objects.get(reference_paiement=transaction_id)
            
            if status == 'ACCEPTED' and vente.statut_paiement == 'en_attente':
                vente.statut_paiement = 'paye'
                vente.save()
                
                # C'est maintenant qu'on déduit le stock !
                for ligne in vente.lignes.all():
                    med = ligne.medicament
                    med.quantite_stock -= ligne.quantite
                    med.save()
                    
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'invalid method'}, status=405)
