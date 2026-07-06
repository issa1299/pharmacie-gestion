from django.db import models
from django.contrib.auth.models import User
from medicaments.models import Medicament
from clients.models import Client

class Vente(models.Model):
    STATUT_CHOICES = [
        ('validee', 'Validée'),
        ('annulee', 'Annulée'),
    ]
    client = models.ForeignKey(
        Client, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='ventes'
    )
    utilisateur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )
    numero_facture = models.CharField(max_length=50, unique=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='validee')
    date_vente = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.numero_facture

    class Meta:
        ordering = ['-date_vente']


class LigneVente(models.Model):
    vente = models.ForeignKey(
        Vente, on_delete=models.CASCADE, related_name='lignes'
    )
    medicament = models.ForeignKey(
        Medicament, on_delete=models.RESTRICT
    )
    quantite = models.IntegerField()
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    sous_total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.sous_total = self.quantite * self.prix_unitaire
        super().save(*args, **kwargs)