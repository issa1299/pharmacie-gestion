from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.db.models.deletion import ProtectedError, RestrictedError
from .models import Medicament, Categorie, Etagere
from .forms import MedicamentForm, EtagereForm
from accounts.permissions import pharmacien_required


# ── Médicaments ───────────────────────────────────────────────────────────────

@login_required
def liste_medicaments(request):
    medicaments = (
        Medicament.objects.select_related('categorie', 'etagere')
        .order_by('nom')
    )
    q = request.GET.get('q', '').strip()
    if q:
        medicaments = medicaments.filter(
            Q(nom__icontains=q) | Q(code_barre__icontains=q)
        )
    categorie_id = request.GET.get('categorie', '')
    if categorie_id:
        medicaments = medicaments.filter(categorie_id=categorie_id)
    etagere_id = request.GET.get('etagere', '')
    if etagere_id:
        medicaments = medicaments.filter(etagere_id=etagere_id)
    paginator = Paginator(medicaments, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'medicaments/liste.html', {
        'medicaments': page_obj,
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
        form = MedicamentForm(request.POST, request.FILES)
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
        form = MedicamentForm(request.POST, request.FILES, instance=medicament)
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


@login_required
@pharmacien_required
def modifier_categorie(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description', '')
        if nom:
            categorie.nom = nom
            categorie.description = description
            categorie.save()
            messages.success(request, "Catégorie modifiée avec succès !")
        return redirect('medicaments:categories')
    return render(request, 'medicaments/categorie_form.html', {
        'categorie': categorie,
    })


@login_required
@pharmacien_required
def supprimer_categorie(request, pk):
    categorie = get_object_or_404(Categorie, pk=pk)
    if request.method == 'POST':
        if categorie.medicaments.exists():
            messages.error(
                request,
                f"Impossible de supprimer '{categorie.nom}' : elle contient encore des médicaments."
            )
            return redirect('medicaments:categories')
        categorie.delete()
        messages.success(request, "Catégorie supprimée.")
        return redirect('medicaments:categories')
    return render(request, 'medicaments/categorie_supprimer.html', {
        'categorie': categorie,
    })


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


# ── Import / Export CSV ──────────────────────────────────────────────────────

@login_required
@pharmacien_required
def telecharger_modele_csv(request):
    """Télécharger un fichier CSV template pré-rempli avec des exemples."""
    import csv
    from django.http import HttpResponse
    resp = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    resp['Content-Disposition'] = 'attachment; filename="modele_medicaments.csv"'
    resp.write('\ufeff')
    writer = csv.writer(resp, delimiter=';', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
        'Nom', 'Categorie', 'Code-barres', 'Description',
        'Prix achat', 'Prix vente', 'Stock', 'Seuil alerte',
        'Date expiration (JJ/MM/AAAA)', 'Etagere (code)',
    ])
    examples = [
        ['Doliprane 1000mg', 'Antalgiques', '3400930000001', 'Paracetamol 1g - boite de 8', '150', '350', '50', '10', '31/12/2027', ''],
        ['Amoxicilline 1g', 'Antibiotiques', '3400930000002', 'Antibiotique large spectre', '800', '1500', '30', '5', '15/06/2027', 'A1'],
        ['Spasfon 80mg', 'Antispasmodiques', '3400930000003', 'Phloroglucinol - tubes de 20', '400', '900', '25', '8', '01/03/2028', 'A2'],
    ]
    for row in examples:
        writer.writerow(row)
    return resp


@login_required
@pharmacien_required
def importer_medicaments_csv(request):
    """Importer des medicaments depuis un fichier CSV."""
    import csv
    import io
    from datetime import datetime
    from django.utils import timezone

    if request.method != 'POST':
        return render(request, 'medicaments/importer.html')

    fichier = request.FILES.get('fichier')
    if not fichier:
        messages.error(request, "Veuillez selectionner un fichier CSV.")
        return render(request, 'medicaments/importer.html')

    if not fichier.name.endswith('.csv'):
        messages.error(request, "Le fichier doit etre au format CSV.")
        return render(request, 'medicaments/importer.html')

    try:
        content = fichier.read().decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(content), delimiter=';')
    except Exception:
        messages.error(request, "Impossible de lire le fichier. Verifiez l'encodage (UTF-8).")
        return render(request, 'medicaments/importer.html')

    crees = 0
    modifies = 0
    erreurs = []

    for i, row in enumerate(reader, start=2):
        try:
            nom = row.get('Nom', '').strip()
            if not nom:
                erreurs.append(f"Ligne {i} : nom vide, ignoree.")
                continue

            categorie = None
            cat_nom = row.get('Categorie', '').strip()
            if cat_nom:
                categorie, _ = Categorie.objects.get_or_create(nom=cat_nom)

            etagere = None
            et_code = row.get('Etagere (code)', '').strip()
            if et_code:
                etagere = Etagere.objects.filter(code=et_code).first()

            prix_achat = float(row.get('Prix achat', '0') or '0')
            prix_vente = float(row.get('Prix vente', '0') or '0')
            stock = int(row.get('Stock', '0') or '0')
            seuil = int(row.get('Seuil alerte', '10') or '10')

            date_exp = None
            date_str = row.get('Date expiration (JJ/MM/AAAA)', '').strip()
            if date_str:
                try:
                    date_exp = datetime.strptime(date_str, '%d/%m/%Y').date()
                except ValueError:
                    try:
                        date_exp = datetime.strptime(date_str, '%Y-%m-%d').date()
                    except ValueError:
                        erreurs.append(f"Ligne {i} : date d'expiration invalide '{date_str}'.")

            code_barre = row.get('Code-barres', '').strip()
            description = row.get('Description', '').strip()

            # Creer ou mettre a jour (selon nom)
            med, created = Medicament.objects.update_or_create(
                nom=nom,
                defaults={
                    'categorie': categorie,
                    'etagere': etagere,
                    'code_barre': code_barre,
                    'description': description,
                    'prix_achat': prix_achat,
                    'prix_vente': prix_vente,
                    'quantite_stock': stock,
                    'seuil_alerte': seuil,
                    'date_expiration': date_exp,
                }
            )
            if created:
                crees += 1
            else:
                modifies += 1

        except Exception as e:
            erreurs.append(f"Ligne {i} : erreur — {str(e)}")

    msg = f"Import termine : {crees} cree(s), {modifies} modifie(s)."
    if erreurs:
        msg += f" {len(erreurs)} erreur(s)."
    messages.success(request, msg)

    if erreurs:
        for err in erreurs[:10]:
            messages.warning(request, err)

    return redirect('medicaments:liste')
