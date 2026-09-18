from django.urls import path
from . import views
from . import exports

app_name = 'ventes'

urlpatterns = [
    path('', views.liste_ventes, name='liste'),
    path('nouvelle/', views.nouvelle_vente, name='nouvelle'),
    path('<int:pk>/', views.detail_vente, name='detail'),
    path('<int:pk>/facture/pdf/', views.facture_pdf, name='facture_pdf'),
    path('<int:pk>/annuler/', views.annuler_vente, name='annuler'),
    path('<int:pk>/mock-payment/', views.mock_payment, name='mock_payment'),
    path('webhook/', views.webhook_paiement, name='webhook'),

    # ── Exports Excel (.xlsx) ──
    path('export/ventes/', exports.export_ventes_xlsx, name='export_ventes'),
    path('export/medicaments/', exports.export_medicaments_xlsx, name='export_medicaments'),
    path('export/clients/', exports.export_clients_xlsx, name='export_clients'),
    path('export/mouvements/', exports.export_mouvements_xlsx, name='export_mouvements'),
    path('export/vente/<int:pk>/', exports.export_vente_detail_xlsx, name='export_vente_detail'),
]