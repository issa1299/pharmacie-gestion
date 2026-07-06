from django.db import models

class Fournisseur(models.Model):
    nom = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Fournisseur"
        ordering = ['nom']