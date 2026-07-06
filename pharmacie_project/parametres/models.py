from django.db import models

class Parametres(models.Model):
    # Informations pharmacie
    nom_pharmacie  = models.CharField(max_length=200, default='PharmaGest')
    slogan         = models.CharField(max_length=200, blank=True)
    adresse        = models.TextField(blank=True)
    telephone      = models.CharField(max_length=20, blank=True)
    email          = models.EmailField(blank=True)
    logo           = models.ImageField(upload_to='logo/', null=True, blank=True)

    # Apparence
    couleur        = models.CharField(max_length=10, default='#0F6E56')
    langue         = models.CharField(max_length=10, default='fr')
    devise         = models.CharField(max_length=10, default='FCFA')
    format_date    = models.CharField(max_length=20, default='d/m/Y')

    # Sécurité
    session_duree  = models.IntegerField(default=30)  # minutes
    tentatives_max = models.IntegerField(default=5)

    def __str__(self):
        return self.nom_pharmacie

    class Meta:
        verbose_name = "Paramètres"