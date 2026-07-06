from django.db import models
from django.contrib.auth.models import User
from medicaments.models import Medicament

class MouvementStock(models.Model):
    TYPE_CHOICES = [
        ('entree', 'Entrée'),
        ('sortie', 'Sortie'),
        ('ajustement', 'Ajustement'),
    ]

    medicament = models.ForeignKey(
        Medicament, on_delete=models.CASCADE, related_name='mouvements'
    )
    utilisateur = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )
    type_mouvement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    quantite = models.IntegerField()
    motif = models.CharField(max_length=200, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type_mouvement} - {self.medicament.nom} ({self.quantite})"

    class Meta:
        ordering = ['-date']
        verbose_name = "Mouvement de stock"