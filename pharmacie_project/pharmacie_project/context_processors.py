"""
Context processor — injecte le rôle de l'utilisateur dans tous les templates.
Variables disponibles dans tous les templates :
  - user_role  : 'patron' | 'pharmacien' | 'caissier' | None
  - is_patron  : bool
  - is_pharmacien_or_more : bool
"""
from accounts.permissions import get_role, is_patron, is_pharmacien_or_more
from accounts.models import UserProfile


def user_role(request):
    if not request.user.is_authenticated:
        return {
            'user_role': None,
            'is_patron': False,
            'is_pharmacien_or_more': False,
        }

    role = get_role(request.user)
    return {
        'user_role': role,
        'is_patron': is_patron(request.user),
        'is_pharmacien_or_more': is_pharmacien_or_more(request.user),
        'role_label': {
            UserProfile.ROLE_PATRON: 'Patron',
            UserProfile.ROLE_PHARMACIEN: 'Pharmacien',
            UserProfile.ROLE_CAISSIER: 'Caissier',
        }.get(role, 'Utilisateur'),
    }
