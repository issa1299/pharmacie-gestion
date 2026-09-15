from django.db import models
from django.contrib.auth.models import User
from medicaments.models import Medicament
from clients.models import Client


class Vente(models.Model):
    STATUT_CHOICES = [
        ('validee', 'Validée'),
        ('annulee', 'Annulée'),
    ]
    MODE_PAIEMENT_CHOICES = [
        ('especes', 'Espèces'),
        ('orange_money', 'Orange Money'),
        ('moov_money', 'Moov Money'),
        ('carte', 'Carte bancaire'),
    ]
    STATUT_PAIEMENT_CHOICES = [
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('echoue', 'Échoué'),
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
    remise = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    mode_paiement = models.CharField(max_length=20, choices=MODE_PAIEMENT_CHOICES, default='especes')
    statut_paiement = models.CharField(max_length=20, choices=STATUT_PAIEMENT_CHOICES, default='paye')
    reference_paiement = models.CharField(max_length=100, blank=True, null=True)
    # ── Sécurité webhook : signature HMAC propre à chaque vente ──
    secret_webhook = models.CharField(max_length=64, blank=True, null=True)

    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='validee')
    # ── Annulation : motif + date remettent le stock ──
    motif_annulation = models.CharField(max_length=255, blank=True, default='')
    date_annulation = models.DateTimeField(null=True, blank=True)
    date_vente = models.DateTimeField(auto_now_add=True)

    @property
    def net_a_payer(self):
        return self.total - self.remise

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
