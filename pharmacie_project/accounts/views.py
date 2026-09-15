from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string

from .models import PasswordResetCode, UserProfile


def get_user_role(user):
    if user.is_superuser:
        return UserProfile.ROLE_PATRON
    profile, _ = UserProfile.objects.get_or_create(user=user)
    return profile.role


def is_patron(user):
    return user.is_authenticated and (
        user.is_superuser or get_user_role(user) == UserProfile.ROLE_PATRON
    )


def role_context(extra=None):
    context = {'roles': UserProfile.ROLE_CHOICES}
    if extra:
        context.update(extra)
    return context


@login_required
def liste_utilisateurs(request):
    if not is_patron(request.user):
        messages.error(request, "Accès refusé !")
        return redirect('dashboard')

    utilisateurs = User.objects.select_related('profile').all().order_by('-date_joined')
    return render(request, 'accounts/liste.html', {'utilisateurs': utilisateurs})


@login_required
def ajouter_utilisateur(request):
    if not is_patron(request.user):
        messages.error(request, "Accès refusé !")
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email', '')
        prenom = request.POST.get('first_name', '')
        nom = request.POST.get('last_name', '')
        role = request.POST.get('role', UserProfile.ROLE_CAISSIER)
        telephone = request.POST.get('telephone', '')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Ce nom d'utilisateur existe déjà !")
            return render(request, 'accounts/form.html', role_context({
                'titre': 'Ajouter un utilisateur',
            }))

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            first_name=prenom,
            last_name=nom,
        )
        user.is_staff = (role == UserProfile.ROLE_PATRON)
        user.save()
        UserProfile.objects.update_or_create(
            user=user,
            defaults={'role': role, 'telephone': telephone},
        )

        messages.success(request, f"Utilisateur {username} créé avec succès !")
        return redirect('accounts:utilisateurs')

    return render(request, 'accounts/form.html', role_context({
        'titre': 'Ajouter un utilisateur',
    }))


@login_required
def modifier_utilisateur(request, pk):
    if not is_patron(request.user):
        messages.error(request, "Accès refusé !")
        return redirect('dashboard')

    utilisateur = get_object_or_404(User, pk=pk)
    profile, _ = UserProfile.objects.get_or_create(user=utilisateur)

    if request.method == 'POST':
        utilisateur.email = request.POST.get('email', '')
        utilisateur.first_name = request.POST.get('first_name', '')
        utilisateur.last_name = request.POST.get('last_name', '')
        role = request.POST.get('role', UserProfile.ROLE_CAISSIER)
        utilisateur.is_staff = (role == UserProfile.ROLE_PATRON)
        utilisateur.is_active = request.POST.get('is_active') == 'on'

        nouveau_mdp = request.POST.get('password')
        if nouveau_mdp:
            utilisateur.set_password(nouveau_mdp)

        utilisateur.save()
        profile.role = role
        profile.telephone = request.POST.get('telephone', '')
        profile.save()

        messages.success(request, "Utilisateur modifié avec succès !")
        return redirect('accounts:utilisateurs')

    return render(request, 'accounts/form.html', role_context({
        'titre': f'Modifier - {utilisateur.username}',
        'utilisateur': utilisateur,
    }))


@login_required
def supprimer_utilisateur(request, pk):
    if not is_patron(request.user):
        messages.error(request, "Accès refusé !")
        return redirect('dashboard')

    utilisateur = get_object_or_404(User, pk=pk)
    if utilisateur == request.user:
        messages.error(request, "Vous ne pouvez pas supprimer votre propre compte !")
        return redirect('accounts:utilisateurs')

    if request.method == 'POST':
        utilisateur.delete()
        messages.success(request, "Utilisateur supprimé.")
        return redirect('accounts:utilisateurs')

    return render(request, 'accounts/confirmer_suppression.html', {
        'utilisateur': utilisateur,
    })


def reset_mot_de_passe_demande(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()

        try:
            user = User.objects.filter(email=email).first()

            if not user:
                messages.error(request, "Aucun compte trouvé avec cet email.")
                return render(request, 'account/reset_demande.html')

            reset_code = PasswordResetCode.create_for_user(user)
            subject = "Code de réinitialisation de mot de passe - PharmaGest"
            html_message = render_to_string('account/email_reset_code.html', {
                'user': user,
                'code': reset_code.code,
            })
            plain_message = f"Votre code de réinitialisation: {reset_code.code}\nValable 15 minutes."

            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, f"Un code a été envoyé à {email}")
            return redirect('account_verify_code')

        except Exception as exc:
            messages.error(request, f"Erreur: {exc}")

    return render(request, 'account/reset_demande.html')


def reset_mot_de_passe_verifier(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        code = request.POST.get('code', '').strip()

        try:
            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, "Email non trouvé.")
                return redirect('account_verify_code')

            reset_code = PasswordResetCode.objects.filter(user=user, code=code).first()
            if not reset_code:
                messages.error(request, "Email ou code incorrect.")
                return render(request, 'account/reset_verifier.html')

            if not reset_code.is_valid():
                messages.error(request, "Code invalide ou expiré.")
                return redirect('account_verify_code')

            request.session['reset_email'] = email
            request.session['reset_code'] = code

            messages.success(request, "Code valide ! Créez un nouveau mot de passe.")
            return redirect('account_new_password')

        except Exception as exc:
            messages.error(request, f"Erreur: {exc}")

    return render(request, 'account/reset_verifier.html')


def reset_mot_de_passe_nouveau(request):
    email = request.session.get('reset_email')
    code = request.session.get('reset_code')

    if not email or not code:
        messages.error(request, "Accès refusé. Veuillez recommencer.")
        return redirect('account_reset_password_request')

    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas !")
            return render(request, 'account/reset_nouveau.html')

        if len(new_password) < 6:
            messages.error(request, "Le mot de passe doit contenir au moins 6 caractères.")
            return render(request, 'account/reset_nouveau.html')

        try:
            user = User.objects.filter(email=email).first()
            if not user:
                messages.error(request, "Erreur. Recommencez.")
                return redirect('account_reset_password_request')

            reset_code = PasswordResetCode.objects.filter(user=user, code=code).first()
            if not reset_code:
                messages.error(request, "Code introuvable. Recommencez.")
                return redirect('account_reset_password_request')

            if not reset_code.is_valid():
                messages.error(request, "Code expiré. Recommencez.")
                return redirect('account_reset_password_request')

            user.set_password(new_password)
            user.save()
            reset_code.is_used = True
            reset_code.save()

            del request.session['reset_email']
            del request.session['reset_code']

            messages.success(request, "Mot de passe changé avec succès ! Connectez-vous.")
            return redirect('account_login')

        except Exception as exc:
            messages.error(request, f"Erreur: {exc}")

    return render(request, 'account/reset_nouveau.html')


def reset_mot_de_passe(request):
    """Réinitialisation DIRECTE (sans code par email).

    Formulaire: email + new_password + confirm_password.
    """
    # SECURITE : le reset direct (sans email/code) n'est autorisé qu'en dev
    # (DEBUG=True). En production il redirige vers le flux par email + code,
    # sinon n'importe qui pourrait changer le mot de passe de n'importe quel compte.
    if not settings.DEBUG:
        return redirect('account_reset_password_request')

    if request.method == 'POST':
        # Le template utilise "identifiant" (email ou username).
        identifiant = request.POST.get('identifiant', '').strip()
        email = request.POST.get('email', '').strip()  # fallback si besoin
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()

        login_value = identifiant or email

        if not login_value:
            messages.error(request, "Veuillez saisir votre email ou nom d'utilisateur.")
            return render(request, 'account/reset_mot_de_passe.html')

        if new_password != confirm_password:
            messages.error(request, "Les mots de passe ne correspondent pas !")
            return render(request, 'account/reset_mot_de_passe.html', {'email': login_value})


        if len(new_password) < 6:
            messages.error(request, "Le mot de passe doit contenir au moins 6 caractères.")
            return render(request, 'account/reset_mot_de_passe.html', {'email': email})

        # Cherche soit par email, soit par username (si le champ "identifiant" est un nom d'utilisateur)
        if login_value and '@' in login_value:
            user = User.objects.filter(email=login_value).first()
        else:
            user = User.objects.filter(username=login_value).first()

        if not user:
            messages.error(request, "Aucun compte trouvé.")
            return render(request, 'account/reset_mot_de_passe.html', {'email': login_value})


        user.set_password(new_password)
        user.save()

        messages.success(request, "Mot de passe changé avec succès ! Connectez-vous.")
        return redirect('account_login')

    return render(request, 'account/reset_mot_de_passe.html')

