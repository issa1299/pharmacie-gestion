from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.liste_stock, name='liste'),
    path('mouvements/', views.liste_mouvements, name='mouvements'),
    path('mouvements/ajouter/', views.ajouter_mouvement, name='ajouter_mouvement'),
]