from django.urls import path
from . import views

app_name = 'medicaments'

urlpatterns = [
    path('', views.liste_medicaments, name='liste'),
    path('ajouter/', views.ajouter_medicament, name='ajouter'),
    path('<int:pk>/modifier/', views.modifier_medicament, name='modifier'),
    path('<int:pk>/supprimer/', views.supprimer_medicament, name='supprimer'),
    path('categories/', views.liste_categories, name='categories'),
    path('categories/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),
    path('categories/<int:pk>/modifier/', views.modifier_categorie, name='modifier_categorie'),
    path('categories/<int:pk>/supprimer/', views.supprimer_categorie, name='supprimer_categorie'),
    path('etageres/', views.liste_etageres, name='etageres'),
    path('etageres/ajouter/', views.ajouter_etagere, name='ajouter_etagere'),
    path('etageres/<int:pk>/modifier/', views.modifier_etagere, name='modifier_etagere'),
    path('etageres/<int:pk>/supprimer/', views.supprimer_etagere, name='supprimer_etagere'),
    path('importer/', views.importer_medicaments_csv, name='importer'),
    path('modele-csv/', views.telecharger_modele_csv, name='modele_csv'),
]