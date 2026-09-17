from django.urls import path
from . import views

app_name = 'fournisseurs'

urlpatterns = [
    path('', views.liste_fournisseurs, name='liste'),
    path('ajouter/', views.ajouter_fournisseur, name='ajouter'),
    path('<int:pk>/', views.detail_fournisseur, name='detail'),
    path('<int:pk>/modifier/', views.modifier_fournisseur, name='modifier'),
    path('<int:pk>/supprimer/', views.supprimer_fournisseur, name='supprimer'),
]