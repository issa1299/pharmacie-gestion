from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F
from medicaments.models import Medicament
from .models import MouvementStock
from .forms import MouvementStockForm
from accounts.permissions import pharmacien_required


@login_required
@pharmacien_required
def liste_stock(request):
    medicaments = Medicament.objects.select_related('categorie').all()
    stock_faible = medicaments.filter(quantite_stock__lte=F('seuil_alerte'))
    return render(request, 'stock/liste.html', {
        'medicaments': medicaments,
        'stock_faible': stock_faible,
    })

@login_required
@pharmacien_required
def liste_mouvements(request):
    mouvements = MouvementStock.objects.select_related(
        'medicament', 'utilisateur'
    ).all()[:50]
    return render(request, 'stock/mouvements.html', {
        'mouvements': mouvements,
    })

@login_required
@pharmacien_required
def ajouter_mouvement(request):
    if request.method == 'POST':
        form = MouvementStockForm(request.POST)
        if form.is_valid():
            mouvement = form.save(commit=False)
            mouvement.utilisateur = request.user
            med = mouvement.medicament
            # Vérifier stock suffisant pour sortie
            if mouvement.type_mouvement == 'sortie':
                if mouvement.quantite > med.quantite_stock:
                    messages.error(request, f"Stock insuffisant ! Stock disponible : {med.quantite_stock}")
                    return render(request, 'stock/mouvement_form.html', {'form': form})
            # Mettre à jour le stock
            if mouvement.type_mouvement == 'entree':
                med.quantite_stock += mouvement.quantite
            elif mouvement.type_mouvement == 'sortie':
                med.quantite_stock -= mouvement.quantite
            elif mouvement.type_mouvement == 'ajustement':
                med.quantite_stock = mouvement.quantite
            med.save()
            mouvement.save()
            messages.success(request, "Mouvement enregistré avec succès !")
            return redirect('stock:liste')
    else:
        form = MouvementStockForm()
    return render(request, 'stock/mouvement_form.html', {'form': form})