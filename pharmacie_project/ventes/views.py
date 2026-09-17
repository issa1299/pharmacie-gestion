from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import F, Q
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from .models import Vente, LigneVente
from medicaments.models import Medicament, Categorie
from clients.models import Client
from parametres.models import Parametres
from accounts.permissions import pharmacien_required


def generer_numero_facture():
    """Génère un numéro unique — verrouille la table pour éviter les doublons
    en cas de ventes simultanées (2 caissiers au même moment)."""
    annee = timezone.now().year
    with transaction.atomic():
        derniers = (
            Vente.objects.select_for_update()
            .filter(date_vente__year=annee, numero_facture__startswith=f"FACT-{annee}-")
            .order_by('-numero_facture')
        )
        if derniers.exists():
            try:
                dernier_num = int(derniers.first().numero_facture.split('-')[-1])
            except (ValueError, IndexError):
                dernier_num = Vente.objects.filter(date_vente__year=annee).count()
        else:
            dernier_num = 0
        return f"FACT-{annee}-{dernier_num + 1:04d}"


@login_required
def liste_ventes(request):
    ventes = (
        Vente.objects.select_related('client', 'utilisateur')
        .order_by('-date_vente')
    )
    q = request.GET.get('q', '').strip()
    if q:
        ventes = ventes.filter(
            Q(numero_facture__icontains=q) |
            Q(client__nom__icontains=q) |
            Q(client__prenom__icontains=q)
        )
    statut_filtre = request.GET.get('statut', '')
    if statut_filtre in ('validee', 'annulee'):
        ventes = ventes.filter(statut=statut_filtre)
    # ── Pagination : 20 ventes par page ──
    paginator = Paginator(ventes, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'ventes/liste.html', {
        'ventes': page_obj,
        'q': q,
        'statut_filtre': statut_filtre,
    })

@login_required
def nouvelle_vente(request):
    medicaments = Medicament.objects.filter(quantite_stock__gt=0).order_by('nom')
    clients = Client.objects.all().order_by('nom')
    categories = Categorie.objects.all()
    contexte = {
        'medicaments': medicaments,
        'clients': clients,
        'categories': categories,
    }

    if request.method == 'POST':
        client_id = request.POST.get('client') or None
        medicament_ids = request.POST.getlist('medicament_id')
        quantites = request.POST.getlist('quantite')

        mode_paiement = request.POST.get('mode_paiement', 'especes')
        try:
            remise = Decimal(str(request.POST.get('remise', 0) or 0))
        except InvalidOperation:
            remise = Decimal('0')
        if remise < 0:
            remise = Decimal('0')

        if not medicament_ids:
            messages.error(request, "Ajoutez au moins un médicament !")
            return render(request, 'ventes/nouvelle.html', contexte)

        # ── Validation stricte AVANT toute écriture ──
        lignes_valides = []
        for med_id, qte_brute in zip(medicament_ids, quantites):
            try:
                qte = int(qte_brute)
            except (ValueError, TypeError):
                messages.error(request, "Quantité invalide détectée !")
                return render(request, 'ventes/nouvelle.html', contexte)
            if qte <= 0:
                messages.error(request, "Les quantités doivent être supérieures à zéro !")
                return render(request, 'ventes/nouvelle.html', contexte)
            try:
                med = Medicament.objects.select_for_update().get(pk=med_id)
            except Medicament.DoesNotExist:
                messages.error(request, "Un médicament sélectionné n'existe plus !")
                return render(request, 'ventes/nouvelle.html', contexte)
            if qte > med.quantite_stock:
                messages.error(
                    request,
                    f"Stock insuffisant pour {med.nom} (dispo : {med.quantite_stock}) !"
                )
                return render(request, 'ventes/nouvelle.html', contexte)
            lignes_valides.append((med, qte))

        total = sum(Decimal(med.prix_vente) * qte for med, qte in lignes_valides)
        # ── Remise plafonnée au total (pas de net à payer négatif) ──
        if remise > total:
            messages.warning(
                request,
                f"Remise plafonnée au total de la vente ({total} FCFA)."
            )
            remise = total

        # ── Création atomique : tout réussit ou rien n'est écrit ──
        try:
            with transaction.atomic():
                vente = Vente.objects.create(
                    client_id=client_id,
                    utilisateur=request.user,
                    numero_facture=generer_numero_facture(),
                    total=total,
                    remise=remise,
                    mode_paiement=mode_paiement,
                    statut_paiement='paye' if mode_paiement == 'especes' else 'en_attente'
                )
                for med, qte in lignes_valides:
                    ligne = LigneVente(
                        vente=vente,
                        medicament=med,
                        quantite=qte,
                        prix_unitaire=med.prix_vente,
                    )
                    ligne.save()  # calcule sous_total
                    # Stock déduit UNIQUEMENT si espèces.
                    # Mobile money / carte : déduction à la réception du webhook.
                    if mode_paiement == 'especes':
                        Medicament.objects.filter(pk=med.pk).update(
                            quantite_stock=F('quantite_stock') - qte
                        )
        except Exception:
            messages.error(request, "Erreur lors de l'enregistrement — réessayez.")
            return render(request, 'ventes/nouvelle.html', contexte)

        if mode_paiement != 'especes':
            from .services.payment import initier_paiement
            url_paiement = initier_paiement(vente)
            return redirect(url_paiement)
        messages.success(request, f"Vente {vente.numero_facture} enregistrée !")
        return redirect('ventes:detail', pk=vente.pk)

    return render(request, 'ventes/nouvelle.html', contexte)

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

@login_required
@pharmacien_required
def annuler_vente(request, pk):
    """Annule une vente validée et remet les quantités en stock."""
    vente = get_object_or_404(Vente, pk=pk)
    if vente.statut == 'annulee':
        messages.info(request, f"La vente {vente.numero_facture} est déjà annulée.")
        return redirect('ventes:detail', pk=vente.pk)
    if request.method == 'POST':
        motif = request.POST.get('motif', '').strip()
        with transaction.atomic():
            vente = Vente.objects.select_for_update().get(pk=pk)
            if vente.statut == 'annulee':
                messages.info(request, "Vente déjà annulée.")
                return redirect('ventes:detail', pk=vente.pk)
            # Remettre le stock — sauf si mobile money jamais payé
            # (la vente 'en_attente' n'avait pas déduit de stock)
            if vente.mode_paiement == 'especes' or vente.statut_paiement == 'paye':
                for ligne in vente.lignes.select_related('medicament').all():
                    Medicament.objects.filter(pk=ligne.medicament_id).update(
                        quantite_stock=F('quantite_stock') + ligne.quantite
                    )
            vente.statut = 'annulee'
            vente.motif_annulation = motif
            vente.date_annulation = timezone.now()
            vente.save(update_fields=['statut', 'motif_annulation', 'date_annulation'])
        messages.success(request, f"Vente {vente.numero_facture} annulée — stock restauré.")
        return redirect('ventes:detail', pk=vente.pk)
    return render(request, 'ventes/annuler.html', {'vente': vente})


# ── PAIMENT API (MOCK) ────────────────────────────────────────────────────────

@login_required
def mock_payment(request, pk):
    """
    Page fictive simulant l'interface de CinetPay / PaySika.
    Signe le callback webhook avec HMAC (comme le ferait le vrai agrégateur).
    """
    vente = get_object_or_404(Vente, pk=pk)
    ref = request.GET.get('ref')

    if request.method == 'POST':
        # On simule le webhook envoyé par l'agrégateur en arrière-plan
        import requests
        from django.urls import reverse
        webhook_url = request.build_absolute_uri(reverse('ventes:webhook'))
        # Appel asynchrone / background normalement, ici synchrone pour tester
        # ── Simule un vrai agrégateur : il signe l'appel avec le secret ──
        try:
            import hashlib as _hashlib
            import hmac as _hmac
            _sig = _hmac.new(
                (vente.secret_webhook or '').encode(),
                f"{ref}:ACCEPTED".encode(),
                _hashlib.sha256,
            ).hexdigest()
            requests.post(
                webhook_url,
                json={'transaction_id': ref, 'status': 'ACCEPTED', 'signature': _sig},
                timeout=10,
            )
        except Exception:
            pass  # Ignorer les erreurs réseau locales
            
        messages.success(request, "Paiement réussi via l'API !")
        return redirect('ventes:detail', pk=vente.pk)
        
    return render(request, 'ventes/mock_payment.html', {'vente': vente, 'ref': ref})

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import hashlib
import hmac
import json
import secrets


def _signature_webhook(secret, transaction_id, status):
    """Calcule la signature HMAC-SHA256 attendue pour un webhook."""
    message = f"{transaction_id}:{status}".encode()
    return hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


@csrf_exempt
@require_POST
def webhook_paiement(request):
    """
    URL appelée par l'agrégateur (CinetPay, etc.) quand un paiement aboutit.
    SÉCURISÉ : vérifie la signature HMAC de chaque appel.
    """
    try:
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        status = data.get('status')
        signature = data.get('signature', '')

        if not transaction_id or not status:
            return JsonResponse({'status': 'error', 'message': 'Données manquantes'}, status=400)

        # Chercher la vente correspondante
        try:
            vente = Vente.objects.get(reference_paiement=transaction_id)
        except Vente.DoesNotExist:
            # Référence inconnue → on répond 'ok' sans rien faire
            # (évite de révéler quelles références existent à un attaquant)
            return JsonResponse({'status': 'ok'})

        # ── Vérification HMAC : bloque les appels forgés ──
        attendue = _signature_webhook(
            vente.secret_webhook or '', transaction_id, status
        )
        if not secrets.compare_digest(str(signature), attendue):
            return JsonResponse(
                {'status': 'error', 'message': 'Signature invalide'}, status=403
            )

        if status == 'ACCEPTED' and vente.statut_paiement == 'en_attente':
            with transaction.atomic():
                vente = Vente.objects.select_for_update().get(pk=vente.pk)
                if vente.statut_paiement != 'en_attente':
                    return JsonResponse({'status': 'ok'})  # déjà traité (idempotent)
                vente.statut_paiement = 'paye'
                vente.save(update_fields=['statut_paiement'])

                # C'est maintenant qu'on déduit le stock !
                for ligne in vente.lignes.all():
                    Medicament.objects.filter(pk=ligne.medicament_id).update(
                        quantite_stock=F('quantite_stock') - ligne.quantite
                    )

        return JsonResponse({'status': 'ok'})
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'JSON invalide'}, status=400)
    except Exception:
        return JsonResponse({'status': 'error', 'message': 'Erreur interne'}, status=400)


# ── FACTURE PDF ───────────────────────────────────────────────────────────────

from io import BytesIO
from django.conf import settings as dj_settings
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


@login_required
def facture_pdf(request, pk):
    """Génère la facture PDF d'une vente (téléchargeable / imprimable)."""
    vente = get_object_or_404(
        Vente.objects.select_related('client', 'utilisateur'), pk=pk
    )
    lignes = vente.lignes.select_related('medicament').all()
    params, _ = Parametres.objects.get_or_create(pk=1)
    devise = params.devise or 'FCFA'

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2 * cm, leftMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'FactureTitle', parent=styles['Heading1'],
        fontSize=20, textColor=colors.HexColor('#0F6E56'),
        alignment=1, spaceAfter=4,
    )
    small = ParagraphStyle('Small', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#555555'))

    elements = []

    # ── En-tête pharmacie (logo si disponible) ──
    logo_img = ''
    if params.logo:
        logo_path = dj_settings.MEDIA_ROOT / params.logo.name
        if logo_path.exists():
            logo_img = Image(str(logo_path), width=3.2 * cm, height=3.2 * cm)
    entete = Table(
        [[logo_img, Paragraph(params.nom_pharmacie, title_style)]],
        colWidths=[3.6 * cm, None],
    )
    entete.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'MIDDLE')]))
    elements.append(entete)
    elements.append(Paragraph(
        f"{params.adresse or ''}"
        + (f" | Tel : {params.telephone}" if params.telephone else "")
        + (f" | {params.email}" if params.email else ""),
        small,
    ))
    elements.append(Spacer(1, 0.5 * cm))

    # ── Infos facture ──
    client_nom = str(vente.client) if vente.client else 'Client anonyme'
    caissier = (
        vente.utilisateur.get_full_name() or vente.utilisateur.username
        if vente.utilisateur else '-'
    )
    infos = Table([
        ['Facture', vente.numero_facture],
        ['Date', vente.date_vente.strftime('%d/%m/%Y %H:%M')],
        ['Client', client_nom],
        ['Caissier', caissier],
        ['Mode de paiement', vente.get_mode_paiement_display()],
        ['Statut paiement', vente.get_statut_paiement_display()],
    ], colWidths=[4.5 * cm, None])
    infos.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9.5),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#666666')),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
    ]))
    elements.append(infos)
    elements.append(Spacer(1, 0.4 * cm))

    # ── Lignes ──
    data = [['Medicament', 'Qte', 'Prix unitaire', f'Sous-total ({devise})']]
    for ligne in lignes:
        data.append([
            ligne.medicament.nom,
            str(ligne.quantite),
            f"{ligne.prix_unitaire:,.2f}".replace(',', ' '),
            f"{ligne.sous_total:,.2f}".replace(',', ' '),
        ])
    table = Table(data, colWidths=[8.2 * cm, 2 * cm, 3.4 * cm, 3.4 * cm], repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F6E56')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D9D9D9')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F6F8F7')]),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.4 * cm))

    # ── Totaux ──
    totaux = Table([
        ['Total', f"{vente.total:,.2f} {devise}".replace(',', ' ')],
        ['Remise', f"-{vente.remise:,.2f} {devise}".replace(',', ' ')],
        ['NET A PAYER', f"{vente.net_a_payer:,.2f} {devise}".replace(',', ' ')],
    ], colWidths=[4.5 * cm, 4.5 * cm], hAlign='RIGHT')
    totaux.setStyle(TableStyle([
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#0F6E56')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.HexColor('#0F6E56')),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(totaux)
    elements.append(Spacer(1, 1 * cm))

    if vente.statut == 'annulee':
        annul_style = ParagraphStyle(
            'Annul', parent=small, textColor=colors.HexColor('#C0392B'), fontSize=10
        )
        elements.append(Paragraph('*** VENTE ANNULEE - FACTURE NON VALABLE ***', annul_style))
    else:
        elements.append(Paragraph('Merci de votre visite !', small))

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="facture_{vente.numero_facture}.pdf"'
    return response
