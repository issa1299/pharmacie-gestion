from django.db import models


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name = "Catégorie"
        ordering = ['nom']


class Etagere(models.Model):
    code        = models.CharField(max_length=20, unique=True)
    nom         = models.CharField(max_length=100)
    couleur     = models.CharField(max_length=10, default='#0C447C')
    icone       = models.CharField(max_length=30, default='bi-capsule')
    emplacement = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.code} — {self.nom}"

    class Meta:
        verbose_name = "Étagère"
        ordering = ['code']


class Medicament(models.Model):
    categorie = models.ForeignKey(
        Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name='medicaments'
    )
    etagere = models.ForeignKey(
        Etagere, on_delete=models.SET_NULL, null=True, blank=True, related_name='medicaments'
    )
    nom = models.CharField(max_length=200)
    code_barre = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    prix_vente = models.DecimalField(max_digits=10, decimal_places=2)
    prix_achat = models.DecimalField(max_digits=10, decimal_places=2)
    date_expiration = models.DateField(null=True, blank=True)
    quantite_stock = models.IntegerField(default=0)
    seuil_alerte = models.IntegerField(default=10)
    # ── Nouveau champ image ──────────────────────────────────────────
    image = models.ImageField(
        upload_to='medicaments/',
        null=True,
        blank=True,
        verbose_name="Photo du médicament"
    )

    def __str__(self):
        return self.nom

    def stock_faible(self):
        return self.quantite_stock <= self.seuil_alerte

    def est_expire(self):
        from django.utils import timezone
        return self.date_expiration and self.date_expiration < timezone.now().date()

    @property
    def image_url(self):
        """Retourne l'URL de l'image ou None si pas d'image."""
        if self.image:
            return self.image.url
        return None

    class Meta:
        verbose_name = "Médicament"
        ordering = ['nom']