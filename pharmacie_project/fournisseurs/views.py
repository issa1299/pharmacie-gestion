from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Fournisseur
from .forms import FournisseurForm
from accounts.permissions import pharmacien_required


@login_required
@pharmacien_required
def liste_fournisseurs(request):
    fournisseurs = Fournisseur.objects.all()
    q = request.GET.get('q', '')
    if q:
        fournisseurs = fournisseurs.filter(
            Q(nom__icontains=q) |
            Q(telephone__icontains=q) |
            Q(email__icontains=q)
        )
    return render(request, 'fournisseurs/liste.html', {
        'fournisseurs': fournisseurs,
        'q': q,
    })


@login_required
@pharmacien_required
def ajouter_fournisseur(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur ajouté avec succès !")
            return redirect('fournisseurs:liste')
    else:
        form = FournisseurForm()
    return render(request, 'fournisseurs/form.html', {
        'form': form,
        'titre': 'Ajouter un fournisseur'
    })


@login_required
@pharmacien_required
def modifier_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            messages.success(request, "Fournisseur modifié !")
            return redirect('fournisseurs:liste')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'fournisseurs/form.html', {
        'form': form,
        'titre': f'Modifier — {fournisseur.nom}'
    })


@login_required
@pharmacien_required
def supprimer_fournisseur(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        messages.success(request, "Fournisseur supprimé.")
        return redirect('fournisseurs:liste')
    return render(request, 'fournisseurs/confirmer_suppression.html', {
        'fournisseur': fournisseur
    })
