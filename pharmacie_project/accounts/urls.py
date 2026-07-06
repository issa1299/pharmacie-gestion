from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('utilisateurs/', views.liste_utilisateurs, name='utilisateurs'),
    path('utilisateurs/ajouter/', views.ajouter_utilisateur, name='ajouter'),
    path('utilisateurs/<int:pk>/modifier/', views.modifier_utilisateur, name='modifier'),
    path('utilisateurs/<int:pk>/supprimer/', views.supprimer_utilisateur, name='supprimer'),
    path('reset-password/', views.reset_mot_de_passe, name='reset_mot_de_passe'),
]