from django.db import models
from django.core.cache import cache

PARAMS_CACHE_KEY = 'pharmacie_params'
PARAMS_CACHE_TTL = 300  # 5 minutes


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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(PARAMS_CACHE_KEY)

    class Meta:
        verbose_name = "Paramètres"

    @classmethod
    def get_cached(cls):
        params = cache.get(PARAMS_CACHE_KEY)
        if params is None:
            params, _ = cls.objects.get_or_create(pk=1)
            cache.set(PARAMS_CACHE_KEY, params, PARAMS_CACHE_TTL)
        return params