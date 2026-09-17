from django.db import models

class Fournisseur(models.Model):
    nom = models.CharField(max_length=200)
    telephone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    adresse = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nom

    def nb_livraisons(self):
        return self.livraisons.filter(type_mouvement='entree').count()

    def total_quantites_livrees(self):
        from django.db.models import Sum
        result = self.livraisons.filter(
            type_mouvement='entree'
        ).aggregate(total=Sum('quantite'))
        return result['total'] or 0

    def medicaments_livres(self):
        from django.db.models import Count
        return (
            self.livraisons.filter(type_mouvement='entree')
            .values('medicament__nom')
            .annotate(nb=Count('id'))
            .order_by('-nb')
        )

    def derniere_livraison(self):
        return self.livraisons.filter(type_mouvement='entree').order_by('-date').first()

    class Meta:
        verbose_name = "Fournisseur"
        ordering = ['nom']