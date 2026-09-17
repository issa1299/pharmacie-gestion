from django.db.models import F
from django.utils import timezone

from medicaments.models import Medicament

from .models import Parametres

TRANSLATIONS = {
    'fr': {
        'tableau_de_bord': 'Tableau de bord',
        'medicaments': 'Médicaments',
        'categories': 'Catégories',
        'etat_du_stock': 'État du stock',
        'mouvements': 'Mouvements',
        'nouvelle_vente': 'Nouvelle vente',
        'historique_ventes': 'Historique ventes',
        'clients': 'Clients',
        'fournisseurs': 'Fournisseurs',
        'statistiques': 'Statistiques',
        'utilisateurs': 'Utilisateurs',
        'parametres': 'Paramètres',
        'principal': 'Principal',
        'catalogue': 'Catalogue',
        'stock': 'Stock',
        'ventes': 'Ventes',
        'gestion': 'Gestion',
        'rapports': 'Rapports',
        'administration': 'Administration',
        'deconnexion': 'Déconnexion',
        'administrateur': 'Administrateur',
        'caissier': 'Caissier',
    },
    'en': {
        'tableau_de_bord': 'Dashboard',
        'medicaments': 'Medicines',
        'categories': 'Categories',
        'etat_du_stock': 'Stock Status',
        'mouvements': 'Movements',
        'nouvelle_vente': 'New Sale',
        'historique_ventes': 'Sales History',
        'clients': 'Customers',
        'fournisseurs': 'Suppliers',
        'statistiques': 'Statistics',
        'utilisateurs': 'Users',
        'parametres': 'Settings',
        'principal': 'Main',
        'catalogue': 'Catalog',
        'stock': 'Stock',
        'ventes': 'Sales',
        'gestion': 'Management',
        'rapports': 'Reports',
        'administration': 'Administration',
        'deconnexion': 'Logout',
        'administrateur': 'Administrator',
        'caissier': 'Cashier',
    },
    'ar': {
        'tableau_de_bord': 'لوحة التحكم',
        'medicaments': 'الأدوية',
        'categories': 'الفئات',
        'etat_du_stock': 'حالة المخزون',
        'mouvements': 'الحركات',
        'nouvelle_vente': 'عملية بيع جديدة',
        'historique_ventes': 'سجل المبيعات',
        'clients': 'العملاء',
        'fournisseurs': 'الموردون',
        'statistiques': 'الإحصائيات',
        'utilisateurs': 'المستخدمون',
        'parametres': 'الإعدادات',
        'principal': 'الرئيسي',
        'catalogue': 'الكتالوج',
        'stock': 'المخزون',
        'ventes': 'المبيعات',
        'gestion': 'الإدارة',
        'rapports': 'التقارير',
        'administration': 'الإدارة',
        'deconnexion': 'تسجيل الخروج',
        'administrateur': 'مسؤول',
        'caissier': 'أمين الصندوق',
    }
}


def site_params(request):
    params = Parametres.get_cached()
    langue = params.langue if params.langue in TRANSLATIONS else 'fr'
    translations = TRANSLATIONS.get(langue, TRANSLATIONS['fr'])
    aujourd_hui = timezone.now().date()

    alertes_stock_count = Medicament.objects.filter(
        quantite_stock__lte=F('seuil_alerte')
    ).count()
    alertes_expiration_count = Medicament.objects.filter(
        date_expiration__isnull=False,
        date_expiration__lte=aujourd_hui
    ).count()

    return {
        "site_params": params,
        "t": translations,
        "langue": langue,
        "alertes_stock_count": alertes_stock_count,
        "alertes_expiration_count": alertes_expiration_count,
        "alertes_total": alertes_stock_count + alertes_expiration_count,
        "alertes_stock_preview": Medicament.objects.filter(
            quantite_stock__lte=F('seuil_alerte')
        ).order_by('quantite_stock', 'nom')[:3],
        "alertes_expiration_preview": Medicament.objects.filter(
            date_expiration__isnull=False,
            date_expiration__lte=aujourd_hui
        ).order_by('date_expiration', 'nom')[:3],
    }
