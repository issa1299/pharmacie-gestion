from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F
from medicaments.models import Medicament
from .models import MouvementStock
from .forms import MouvementStockForm
from accounts.permissions import pharmacien_required


@login_required
@pharmacien_required
def liste_stock(request):
    medicaments = (
        Medicament.objects.select_related('categorie', 'etagere')
        .order_by('nom')
    )
    q = request.GET.get('q', '').strip()
    if q:
        medicaments = medicaments.filter(nom__icontains=q)
    alerte_only = request.GET.get('alerte') == '1'
    if alerte_only:
        medicaments = medicaments.filter(quantite_stock__lte=F('seuil_alerte'))
    nb_alertes = Medicament.objects.filter(
        quantite_stock__lte=F('seuil_alerte')
    ).count()
    paginator = Paginator(medicaments, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'stock/liste.html', {
        'medicaments': page_obj,
        'stock_faible': Medicament.objects.filter(
            quantite_stock__lte=F('seuil_alerte')
        ),
        'nb_alertes': nb_alertes,
        'alerte_only': alerte_only,
        'q': q,
    })

@login_required
@pharmacien_required
def liste_mouvements(request):
    mouvements = MouvementStock.objects.select_related(
        'medicament', 'utilisateur'
    ).order_by('-date')
    type_filtre = request.GET.get('type', '')
    if type_filtre in ('entree', 'sortie', 'ajustement'):
        mouvements = mouvements.filter(type_mouvement=type_filtre)
    paginator = Paginator(mouvements, 25)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'stock/mouvements.html', {
        'mouvements': page_obj,
        'type_filtre': type_filtre,
    })

@login_required
@pharmacien_required
def ajouter_mouvement(request):
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            try:
                qte = int(form.cleaned_data['quantite'])
            except (TypeError, ValueError):
                messages.error(request, "Quantité invalide.")
                return render(request, 'stock/mouvement_form.html', {'form': form})
            if qte <= 0:
                messages.error(request, "La quantité doit être supérieure à zéro.")
                return render(request, 'stock/mouvement_form.html', {'form': form})
            with transaction.atomic():
                med = Medicament.objects.select_for_update().get(
                    pk=form.cleaned_data['medicament'].pk
                )
                type_mvt = form.cleaned_data['type_mouvement']
                if type_mvt == 'sortie' and qte > med.quantite_stock:
                    messages.error(
                        request,
                        f"Stock insuffisant ! Stock disponible : {med.quantite_stock}"
                    )
                    return render(request, 'stock/mouvement_form.html', {'form': form})
                if type_mvt == 'entree':
                    Medicament.objects.filter(pk=med.pk).update(
                        quantite_stock=F('quantite_stock') + qte
                    )
                elif type_mvt == 'sortie':
                    Medicament.objects.filter(pk=med.pk).update(
                        quantite_stock=F('quantite_stock') - qte
                    )
                elif type_mvt == 'ajustement':
                    Medicament.objects.filter(pk=med.pk).update(
                        quantite_stock=qte
                    )
                mouvement = form.save(commit=False)
                mouvement.quantite = qte
                mouvement.utilisateur = request.user
                mouvement.save()
            messages.success(request, "Mouvement enregistré avec succès !")
            return redirect('stock:liste')
    else:
        form = MouvementStockForm()
    return render(request, 'stock/mouvement_form.html', {'form': form})