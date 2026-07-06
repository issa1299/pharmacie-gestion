from datetime import datetime, timedelta
from io import BytesIO
import json

from django.contrib.auth.decorators import login_required
from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from clients.models import Client
from fournisseurs.models import Fournisseur
from medicaments.models import Medicament
from stock.models import MouvementStock
from ventes.models import LigneVente, Vente
from accounts.permissions import pharmacien_required


def calculate_period_stats(date_start, date_end):
    ventes = Vente.objects.filter(
        date_vente__date__gte=date_start,
        date_vente__date__lte=date_end,
        statut='validee',
    )
    return ventes.count(), ventes.aggregate(total=Sum('total'))['total'] or 0


def parse_period(request):
    today = timezone.now().date()
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')

    if date_debut and date_fin:
        try:
            return (
                datetime.strptime(date_debut, '%Y-%m-%d').date(),
                datetime.strptime(date_fin, '%Y-%m-%d').date(),
            )
        except ValueError:
            pass

    return today.replace(day=1), today


def stock_value_queryset(queryset):
    return queryset.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('quantite_stock') * F('prix_achat'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
    )['total'] or 0


def money(value):
    return f'{value or 0:,.0f}'.replace(',', ' ')


def pdf_section(elements, title, styles):
    elements.append(Spacer(1, 0.2 * inch))
    elements.append(Paragraph(title, styles['Heading2']))
    elements.append(Spacer(1, 0.12 * inch))


def pdf_table(elements, data, col_widths=None, font_size=8):
    if len(data) <= 1:
        elements.append(Paragraph('Aucune donnee disponible.', getSampleStyleSheet()['Normal']))
        return

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0F6E56')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), font_size),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D9D9D9')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F6F8F7')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(table)


@login_required
@pharmacien_required
def index(request):
    aujourd_hui = timezone.now().date()
    date_debut, date_fin = parse_period(request)

    ventes_periode = Vente.objects.filter(
        date_vente__date__gte=date_debut,
        date_vente__date__lte=date_fin,
        statut='validee',
    )
    lignes_periode = LigneVente.objects.filter(vente__in=ventes_periode).select_related('medicament', 'vente')

    total_medicaments = Medicament.objects.count()
    total_clients = Client.objects.count()
    total_fournisseurs = Fournisseur.objects.count()
    total_ventes_mois, ca_mois = calculate_period_stats(date_debut, date_fin)

    cout_achats_vendus = lignes_periode.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('quantite') * F('medicament__prix_achat'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
    )['total'] or 0
    benefice_estime = ca_mois - cout_achats_vendus
    valeur_stock = stock_value_queryset(Medicament.objects.all())

    labels_jours = []
    ca_jours = []
    for i in range(6, -1, -1):
        jour = date_fin - timedelta(days=i)
        ca = Vente.objects.filter(date_vente__date=jour, statut='validee').aggregate(total=Sum('total'))['total'] or 0
        labels_jours.append(jour.strftime('%d/%m'))
        ca_jours.append(float(ca))

    top_medicaments = lignes_periode.values('medicament__nom').annotate(
        total_vendu=Sum('quantite')
    ).order_by('-total_vendu')[:5]
    top_noms = [m['medicament__nom'] for m in top_medicaments]
    top_qtes = [m['total_vendu'] for m in top_medicaments]

    ca_categorie = lignes_periode.values('medicament__categorie__nom').annotate(
        total_ca=Sum('sous_total')
    ).order_by('-total_ca')[:8]
    labels_cat = [c['medicament__categorie__nom'] or 'Sans categorie' for c in ca_categorie]
    ca_cat = [float(c['total_ca'] or 0) for c in ca_categorie]

    stock_faible = Medicament.objects.filter(quantite_stock__lte=F('seuil_alerte')).order_by('quantite_stock')[:8]
    stock_rupture = Medicament.objects.filter(quantite_stock__lte=0).order_by('nom')[:8]

    limite_expiration = aujourd_hui + timedelta(days=30)
    medicaments_expires = Medicament.objects.filter(date_expiration__lt=aujourd_hui).order_by('date_expiration')[:8]
    medicaments_expirent_bientot = Medicament.objects.filter(
        date_expiration__gte=aujourd_hui,
        date_expiration__lte=limite_expiration,
    ).order_by('date_expiration')[:8]
    pertes_expiration = stock_value_queryset(Medicament.objects.filter(date_expiration__lt=aujourd_hui))

    mouvements_periode = MouvementStock.objects.filter(
        date__date__gte=date_debut,
        date__date__lte=date_fin,
    ).select_related('medicament', 'utilisateur')
    mouvements_resume = mouvements_periode.values('type_mouvement').annotate(
        total=Count('id'),
        quantite=Sum('quantite'),
    ).order_by('type_mouvement')
    derniers_mouvements = mouvements_periode.order_by('-date')[:10]
    ajustements = mouvements_periode.filter(type_mouvement='ajustement').order_by('-date')[:8]

    labels_semaines = []
    ca_semaines = []
    nb_ventes_semaines = []
    jour_courant = date_debut
    semaine_num = 1

    while jour_courant <= date_fin:
        fin_semaine = min(jour_courant + timedelta(days=6), date_fin)
        nb_ventes, ca = calculate_period_stats(jour_courant, fin_semaine)
        labels_semaines.append(f'Sem {semaine_num}')
        ca_semaines.append(float(ca))
        nb_ventes_semaines.append(nb_ventes)
        jour_courant = fin_semaine + timedelta(days=1)
        semaine_num += 1

    jours_diff = (date_fin - date_debut).days + 1
    ventes_prev, ca_prev = calculate_period_stats(
        date_debut - timedelta(days=jours_diff),
        date_debut - timedelta(days=1),
    )
    variation_ca = ((ca_mois - ca_prev) / ca_prev * 100) if ca_prev > 0 else 0
    variation_ventes = ((total_ventes_mois - ventes_prev) / ventes_prev * 100) if ventes_prev > 0 else 0

    context = {
        'total_medicaments': total_medicaments,
        'total_clients': total_clients,
        'total_fournisseurs': total_fournisseurs,
        'total_ventes_mois': total_ventes_mois,
        'ca_mois': ca_mois,
        'benefice_estime': benefice_estime,
        'cout_achats_vendus': cout_achats_vendus,
        'valeur_stock': valeur_stock,
        'pertes_expiration': pertes_expiration,
        'date_debut': date_debut.strftime('%Y-%m-%d'),
        'date_fin': date_fin.strftime('%Y-%m-%d'),
        'labels_jours': json.dumps(labels_jours),
        'ca_jours': json.dumps(ca_jours),
        'labels_semaines': json.dumps(labels_semaines),
        'ca_semaines': json.dumps(ca_semaines),
        'nb_ventes_semaines': json.dumps(nb_ventes_semaines),
        'labels_cat': json.dumps(labels_cat),
        'ca_cat': json.dumps(ca_cat),
        'top_noms': json.dumps(top_noms),
        'top_qtes': json.dumps(top_qtes),
        'stock_faible': stock_faible,
        'stock_rupture': stock_rupture,
        'medicaments_expires': medicaments_expires,
        'medicaments_expirent_bientot': medicaments_expirent_bientot,
        'mouvements_resume': mouvements_resume,
        'derniers_mouvements': derniers_mouvements,
        'ajustements': ajustements,
        'dernieres_ventes': ventes_periode.select_related('client').order_by('-date_vente')[:10],
        'fournisseurs': Fournisseur.objects.order_by('-created_at')[:8],
        'ca_prev': ca_prev,
        'ventes_prev': ventes_prev,
        'variation_ca': variation_ca,
        'variation_ventes': variation_ventes,
    }
    return render(request, 'rapports/index.html', context)


@login_required
@pharmacien_required
def export_pdf(request):
    date_debut, date_fin = parse_period(request)
    today = timezone.now().date()

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=28,
        leftMargin=28,
        topMargin=28,
        bottomMargin=28,
    )
    elements = []
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#0F6E56'),
        spaceAfter=12,
        alignment=1,
    )
    elements.append(Paragraph('Rapport de gestion pharmacie', title_style))
    elements.append(Paragraph(f"Periode: {date_debut.strftime('%d/%m/%Y')} au {date_fin.strftime('%d/%m/%Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.2 * inch))

    total_ventes, ca_total = calculate_period_stats(date_debut, date_fin)
    ventes = Vente.objects.filter(
        date_vente__date__gte=date_debut,
        date_vente__date__lte=date_fin,
        statut='validee',
    ).select_related('client', 'utilisateur')
    lignes = LigneVente.objects.filter(
        vente__date_vente__date__gte=date_debut,
        vente__date_vente__date__lte=date_fin,
        vente__statut='validee',
    ).select_related('medicament', 'vente')
    cout_achats_vendus = lignes.aggregate(
        total=Sum(
            ExpressionWrapper(
                F('quantite') * F('medicament__prix_achat'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
    )['total'] or 0
    benefice_estime = ca_total - cout_achats_vendus
    valeur_stock = stock_value_queryset(Medicament.objects.all())

    limite_expiration = today + timedelta(days=30)
    stock_faible = Medicament.objects.filter(quantite_stock__lte=F('seuil_alerte')).order_by('quantite_stock')[:12]
    stock_rupture = Medicament.objects.filter(quantite_stock__lte=0).order_by('nom')[:12]
    medicaments_expires = Medicament.objects.filter(date_expiration__lt=today).order_by('date_expiration')[:12]
    medicaments_expirent_bientot = Medicament.objects.filter(
        date_expiration__gte=today,
        date_expiration__lte=limite_expiration,
    ).order_by('date_expiration')[:12]
    pertes_expiration = stock_value_queryset(Medicament.objects.filter(date_expiration__lt=today))

    mouvements = MouvementStock.objects.filter(
        date__date__gte=date_debut,
        date__date__lte=date_fin,
    ).select_related('medicament', 'utilisateur')
    mouvements_resume = mouvements.values('type_mouvement').annotate(
        total=Count('id'),
        quantite=Sum('quantite'),
    ).order_by('type_mouvement')
    ajustements = mouvements.filter(type_mouvement='ajustement').order_by('-date')[:12]

    synthese_data = [
        ['Rubrique', 'Valeur'],
        ['Medicaments', str(Medicament.objects.count())],
        ['Clients', str(Client.objects.count())],
        ['Fournisseurs', str(Fournisseur.objects.count())],
        ['Nombre de ventes', str(total_ventes)],
        ["Chiffre d'affaires", money(ca_total)],
        ["Cout d'achat vendu", money(cout_achats_vendus)],
        ['Benefice estime', money(benefice_estime)],
        ['Valeur du stock', money(valeur_stock)],
        ['Pertes expiration estimees', money(pertes_expiration)],
    ]
    pdf_section(elements, 'Synthese generale', styles)
    pdf_table(elements, synthese_data, [3.3 * inch, 2.1 * inch], font_size=9)
    elements.append(PageBreak())

    pdf_section(elements, 'Rapport des ventes', styles)
    ventes_data = [['Facture', 'Client', 'Caissier', 'Total', 'Date']]
    for vente in ventes.order_by('-date_vente')[:20]:
        ventes_data.append([
            str(vente.numero_facture),
            str(vente.client or 'Anonyme'),
            str(vente.utilisateur or '-'),
            money(vente.total),
            vente.date_vente.strftime('%d/%m/%Y %H:%M'),
        ])
    pdf_table(elements, ventes_data, [1.15 * inch, 1.35 * inch, 1.2 * inch, 0.9 * inch, 1.25 * inch])

    top_data = [['Medicament', 'Quantite vendue', 'Chiffre affaire']]
    for item in lignes.values('medicament__nom').annotate(
        quantite=Sum('quantite'),
        ca=Sum('sous_total'),
    ).order_by('-quantite')[:10]:
        top_data.append([
            item['medicament__nom'],
            str(item['quantite']),
            money(item['ca']),
        ])
    pdf_section(elements, 'Top medicaments vendus', styles)
    pdf_table(elements, top_data, [3 * inch, 1.4 * inch, 1.4 * inch])

    categorie_data = [['Categorie', 'Chiffre affaire']]
    for item in lignes.values('medicament__categorie__nom').annotate(
        ca=Sum('sous_total'),
    ).order_by('-ca')[:10]:
        categorie_data.append([item['medicament__categorie__nom'] or 'Sans categorie', money(item['ca'])])
    pdf_section(elements, 'Chiffre affaire par categorie', styles)
    pdf_table(elements, categorie_data, [3.4 * inch, 2 * inch])
    elements.append(PageBreak())

    pdf_section(elements, 'Rapport du stock', styles)
    stock_data = [['Indicateur', 'Valeur']]
    stock_data.extend([
        ['Medicaments enregistres', str(Medicament.objects.count())],
        ['Stock faible', str(stock_faible.count() if hasattr(stock_faible, 'count') else len(stock_faible))],
        ['Ruptures', str(stock_rupture.count() if hasattr(stock_rupture, 'count') else len(stock_rupture))],
        ['Valeur totale du stock', money(valeur_stock)],
    ])
    pdf_table(elements, stock_data, [3.3 * inch, 2.1 * inch])

    stock_faible_data = [['Medicament', 'Stock', 'Seuil']]
    for med in stock_faible:
        stock_faible_data.append([med.nom, str(med.quantite_stock), str(med.seuil_alerte)])
    pdf_section(elements, 'Medicaments en stock faible', styles)
    pdf_table(elements, stock_faible_data, [3.2 * inch, 1.1 * inch, 1.1 * inch])

    rupture_data = [['Medicament', 'Stock']]
    for med in stock_rupture:
        rupture_data.append([med.nom, str(med.quantite_stock)])
    pdf_section(elements, 'Medicaments en rupture', styles)
    pdf_table(elements, rupture_data, [4 * inch, 1.4 * inch])
    elements.append(PageBreak())

    pdf_section(elements, 'Rapport des expirations', styles)
    expiration_resume = [
        ['Indicateur', 'Valeur'],
        ['Medicaments expires', str(Medicament.objects.filter(date_expiration__lt=today).count())],
        ['Expirent dans 30 jours', str(Medicament.objects.filter(date_expiration__gte=today, date_expiration__lte=limite_expiration).count())],
        ['Pertes estimees', money(pertes_expiration)],
    ]
    pdf_table(elements, expiration_resume, [3.3 * inch, 2.1 * inch])

    expires_data = [['Medicament', 'Stock', 'Date expiration']]
    for med in medicaments_expires:
        expires_data.append([med.nom, str(med.quantite_stock), med.date_expiration.strftime('%d/%m/%Y')])
    pdf_section(elements, 'Medicaments expires', styles)
    pdf_table(elements, expires_data, [3.1 * inch, 1 * inch, 1.4 * inch])

    bientot_data = [['Medicament', 'Stock', 'Date expiration']]
    for med in medicaments_expirent_bientot:
        bientot_data.append([med.nom, str(med.quantite_stock), med.date_expiration.strftime('%d/%m/%Y')])
    pdf_section(elements, 'Medicaments qui expirent bientot', styles)
    pdf_table(elements, bientot_data, [3.1 * inch, 1 * inch, 1.4 * inch])
    elements.append(PageBreak())

    pdf_section(elements, 'Rapport des mouvements', styles)
    mouvement_resume_data = [['Type', 'Nombre', 'Quantite']]
    for item in mouvements_resume:
        mouvement_resume_data.append([
            item['type_mouvement'].title(),
            str(item['total']),
            str(item['quantite'] or 0),
        ])
    pdf_table(elements, mouvement_resume_data, [2.2 * inch, 1.4 * inch, 1.4 * inch])

    mouvements_data = [['Medicament', 'Type', 'Quantite', 'Utilisateur', 'Date']]
    for mouvement in mouvements.order_by('-date')[:20]:
        mouvements_data.append([
            mouvement.medicament.nom,
            mouvement.get_type_mouvement_display(),
            str(mouvement.quantite),
            str(mouvement.utilisateur or '-'),
            mouvement.date.strftime('%d/%m/%Y %H:%M'),
        ])
    pdf_section(elements, 'Derniers mouvements', styles)
    pdf_table(elements, mouvements_data, [2 * inch, 1 * inch, 0.8 * inch, 1.1 * inch, 1.2 * inch])

    ajustements_data = [['Medicament', 'Quantite ajustee', 'Motif', 'Date']]
    for mouvement in ajustements:
        ajustements_data.append([
            mouvement.medicament.nom,
            str(mouvement.quantite),
            mouvement.motif or '-',
            mouvement.date.strftime('%d/%m/%Y %H:%M'),
        ])
    pdf_section(elements, 'Ajustements de stock', styles)
    pdf_table(elements, ajustements_data, [2 * inch, 1.1 * inch, 2 * inch, 1.2 * inch])
    elements.append(PageBreak())

    pdf_section(elements, 'Rapport financier', styles)
    financier_data = [
        ['Indicateur', 'Montant'],
        ["Chiffre d'affaires", money(ca_total)],
        ["Cout d'achat des produits vendus", money(cout_achats_vendus)],
        ['Benefice estime', money(benefice_estime)],
        ['Valeur actuelle du stock', money(valeur_stock)],
        ['Pertes expiration estimees', money(pertes_expiration)],
    ]
    pdf_table(elements, financier_data, [3.5 * inch, 2 * inch])

    pdf_section(elements, 'Rapport fournisseurs', styles)
    fournisseurs_data = [['Nom', 'Telephone', 'Email', 'Ajoute le']]
    for fournisseur in Fournisseur.objects.order_by('-created_at')[:20]:
        fournisseurs_data.append([
            fournisseur.nom,
            fournisseur.telephone or '-',
            fournisseur.email or '-',
            fournisseur.created_at.strftime('%d/%m/%Y'),
        ])
    pdf_table(elements, fournisseurs_data, [1.8 * inch, 1.2 * inch, 1.8 * inch, 1 * inch])

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_{date_debut}_{date_fin}.pdf"'
    return response
