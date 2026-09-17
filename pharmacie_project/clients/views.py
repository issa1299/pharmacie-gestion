from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from .models import Client
from .forms import ClientForm

@login_required
def liste_clients(request):
    clients = Client.objects.annotate(nb_ventes=Count('ventes')).order_by('nom')
    q = request.GET.get('q', '').strip()
    if q:
        clients = clients.filter(
            Q(nom__icontains=q) |
            Q(prenom__icontains=q) |
            Q(telephone__icontains=q) |
            Q(email__icontains=q)
        )
    paginator = Paginator(clients, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'clients/liste.html', {
        'clients': page_obj,
        'q': q,
    })


@login_required
def detail_client(request, pk):
    """Fiche client enrichie : historique d'achats + statistiques."""
    client = get_object_or_404(Client, pk=pk)
    ventes = client.ventes.select_related('utilisateur').order_by('-date_vente')
    stats = ventes.filter(statut='validee').aggregate(
        total_achats=Sum('total'),
        nb_achats=Count('id'),
    )
    paginator = Paginator(ventes, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'clients/detail.html', {
        'client': client,
        'ventes': page_obj,
        'nb_ventes': ventes.count(),
        'total_achats': stats['total_achats'] or 0,
        'nb_achats_valides': stats['nb_achats'] or 0,
    })

@login_required
def ajouter_client(request):
    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Client ajouté avec succès !")
            return redirect('clients:liste')
    else:
        form = ClientForm()
    return render(request, 'clients/form.html', {
        'form': form,
        'titre': 'Ajouter un client'
    })

@login_required
def modifier_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client modifié avec succès !")
            return redirect('clients:liste')
    else:
        form = ClientForm(instance=client)
    return render(request, 'clients/form.html', {
        'form': form,
        'titre': f'Modifier — {client.nom}'
    })

@login_required
def supprimer_client(request, pk):
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.delete()
        messages.success(request, "Client supprimé.")
        return redirect('clients:liste')
    return render(request, 'clients/confirmer_suppression.html', {
        'client': client
    })
