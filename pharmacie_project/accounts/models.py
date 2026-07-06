from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string


class UserProfile(models.Model):
    ROLE_PATRON = 'patron'
    ROLE_PHARMACIEN = 'pharmacien'
    ROLE_CAISSIER = 'caissier'
    ROLE_CHOICES = [
        (ROLE_PATRON, 'Patron'),
        (ROLE_PHARMACIEN, 'Pharmacien'),
        (ROLE_CAISSIER, 'Caissier'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    telephone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CAISSIER)

    def role_label(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'Caissier')

    def __str__(self):
        return f"Profil de {self.user.username}"


class PasswordResetCode(models.Model):
    """Modèle pour gérer les codes de réinitialisation de mot de passe"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='password_reset')
    code = models.CharField(max_length=6, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Code de réinitialisation"
        verbose_name_plural = "Codes de réinitialisation"

    def __str__(self):
        return f"Code pour {self.user.username}"

    @staticmethod
    def generate_code():
        """Génère un code aléatoire à 6 chiffres"""
        return ''.join(random.choices(string.digits, k=6))

    def is_valid(self):
        """Vérifie si le code est valide (non expiré et non utilisé)"""
        return not self.is_used and timezone.now() <= self.expires_at

    @classmethod
    def create_for_user(cls, user):
        """Crée ou met à jour un code pour un utilisateur"""
        code = cls.generate_code()
        expires_at = timezone.now() + timezone.timedelta(minutes=15)
        reset_code, created = cls.objects.update_or_create(
            user=user,
            defaults={
                'code': code,
                'expires_at': expires_at,
                'is_used': False,
            }
        )
        return reset_code