"""
Utilitaires de permissions basés sur les rôles.
Rôles : patron > pharmacien > caissier
"""
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from .models import UserProfile


# ── Helpers ──────────────────────────────────────────────────────────────────

def get_role(user):
    """Retourne le rôle de l'utilisateur (chaîne)."""
    if not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserProfile.ROLE_PATRON
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile.role


def is_caissier(user):
    return get_role(user) in (
        UserProfile.ROLE_CAISSIER,
        UserProfile.ROLE_PHARMACIEN,
        UserProfile.ROLE_PATRON,
    )


def is_pharmacien_or_more(user):
    """True si pharmacien ou patron."""
    return get_role(user) in (UserProfile.ROLE_PHARMACIEN, UserProfile.ROLE_PATRON)


def is_patron(user):
    """True si patron (ou superuser)."""
    return get_role(user) == UserProfile.ROLE_PATRON


# ── Décorateurs ───────────────────────────────────────────────────────────────

def pharmacien_required(view_func):
    """Bloque l'accès si l'utilisateur n'est pas au moins pharmacien."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        if not is_pharmacien_or_more(request.user):
            messages.error(
                request,
                "⛔ Accès refusé — Cette section est réservée aux pharmaciens."
            )
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped


def patron_required(view_func):
    """Bloque l'accès si l'utilisateur n'est pas patron."""
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('account_login')
        if not is_patron(request.user):
            messages.error(
                request,
                "⛔ Accès refusé — Cette section est réservée aux administrateurs."
            )
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped
