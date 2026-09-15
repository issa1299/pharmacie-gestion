from django.urls import path
from . import views

app_name = 'ventes'

urlpatterns = [
    path('', views.liste_ventes, name='liste'),
    path('nouvelle/', views.nouvelle_vente, name='nouvelle'),
    path('<int:pk>/', views.detail_vente, name='detail'),
    path('<int:pk>/facture/pdf/', views.facture_pdf, name='facture_pdf'),
    path('<int:pk>/annuler/', views.annuler_vente, name='annuler'),
    path('<int:pk>/mock-payment/', views.mock_payment, name='mock_payment'),
    path('webhook/', views.webhook_paiement, name='webhook'),
]