from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models.deletion import ProtectedError, RestrictedError
from .models import Medicament, Categorie, Etagere
from .forms import MedicamentForm, EtagereForm
from accounts.permissions import pharmacien_required


# ── Médicaments ───────────────────────────────────────────────────────────────

@login_required
def liste_medicaments(request):
    medicaments = Medicament.objects.select_related('categorie', 'etagere').all()
    q = request.GET.get('q', '')
    if q:
        medicaments = medicaments.filter(nom__icontains=q)
    categorie_id = request.GET.get('categorie', '')
    if categorie_id:
        medicaments = medicaments.filter(categorie_id=categorie_id)
    etagere_id = request.GET.get('etagere', '')
    if etagere_id:
        medicaments = medicaments.filter(etagere_id=etagere_id)
    return render(request, 'medicaments/liste.html', {
        'medicaments': medicaments,
        'categories': Categorie.objects.all(),
        'etageres': Etagere.objects.all(),
        'q': q,
        'categorie_id': categorie_id,
        'etagere_id': etagere_id,
    })


@login_required
@pharmacien_required
def ajouter_medicament(request):
    if request.method == 'POST':
        form = MedicamentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Médicament ajouté avec succès !")
            return redirect('medicaments:liste')
    else:
        form = MedicamentForm()
    return render(request, 'medicaments/form.html', {
        'form': form,
        'titre': 'Ajouter un médicament'
    })


@login_required
@pharmacien_required
def modifier_medicament(request, pk):
    medicament = get_object_or_404(Medicament, pk=pk)
    if request.method == 'POST':
        form = MedicamentForm(request.POST, instance=medicament)
        if form.is_valid():
            form.save()
            messages.success(request, "Médicament modifié !")
            return redirect('medicaments:liste')
    else:
        form = MedicamentForm(instance=medicament)
    return render(request, 'medicaments/form.html', {
        'form': form,
        'titre': f'Modifier — {medicament.nom}'
    })


@login_required
@pharmacien_required
def supprimer_medicament(request, pk):
    medicament = get_object_or_404(Medicament, pk=pk)
    if request.method == 'POST':
        try:
            medicament.delete()
        except (ProtectedError, RestrictedError):
            messages.error(
                request,
                "Impossible de supprimer ce médicament car il est déjà utilisé dans une vente."
            )
            return redirect('medicaments:liste')
        messages.success(request, "Médicament supprimé.")
        return redirect('medicaments:liste')
    return render(request, 'medicaments/comfirmer_supprimer.html', {
        'medicament': medicament
    })


# ── Catégories ────────────────────────────────────────────────────────────────

@login_required
def liste_categories(request):
    categories = Categorie.objects.all()
    return render(request, 'medicaments/categories.html', {
        'categories': categories
    })


@login_required
@pharmacien_required
def ajouter_categorie(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description', '')
        if nom:
            Categorie.objects.create(nom=nom, description=description)
            messages.success(request, "Catégorie ajoutée avec succès !")
        return redirect('medicaments:categories')
    return redirect('medicaments:categories')


# ── Étagères ──────────────────────────────────────────────────────────────────

@login_required
def liste_etageres(request):
    etageres = Etagere.objects.all()
    return render(request, 'medicaments/etageres.html', {'etageres': etageres})


@login_required
@pharmacien_required
def ajouter_etagere(request):
    if request.method == 'POST':
        form = EtagereForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Étagère ajoutée avec succès !")
            return redirect('medicaments:etageres')
    else:
        form = EtagereForm()
    return render(request, 'medicaments/etagere_form.html', {
        'form': form, 'titre': 'Ajouter une étagère'
    })


@login_required
@pharmacien_required
def modifier_etagere(request, pk):
    etagere = get_object_or_404(Etagere, pk=pk)
    if request.method == 'POST':
        form = EtagereForm(request.POST, instance=etagere)
        if form.is_valid():
            form.save()
            messages.success(request, "Étagère modifiée !")
            return redirect('medicaments:etageres')
    else:
        form = EtagereForm(instance=etagere)
    return render(request, 'medicaments/etagere_form.html', {
        'form': form, 'titre': f'Modifier — {etagere.code}'
    })


@login_required
@pharmacien_required
def supprimer_etagere(request, pk):
    etagere = get_object_or_404(Etagere, pk=pk)
    if request.method == 'POST':
        etagere.delete()
        messages.success(request, "Étagère supprimée.")
        return redirect('medicaments:etageres')
    return render(request, 'medicaments/etagere_supprimer.html', {'etagere': etagere})
