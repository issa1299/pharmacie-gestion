from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .forms import ParametresForm
import os
import json
from .models import Parametres

@login_required
def parametres(request):
    if not request.user.is_staff:
        messages.error(request, "Accès refusé !")
        return redirect('dashboard')

    params, _ = Parametres.objects.get_or_create(pk=1)

    if request.method == 'POST':
        # On garde une référence de l'ancien logo avant modification
        old_logo_path = None
        old_has_logo = bool(params.logo)
        if params.logo:
            try:
                old_logo_path = params.logo.path
            except ValueError:
                old_logo_path = None

        form = ParametresForm(request.POST, request.FILES, instance=params)

        # Gestion du mot de passe séparément
        new_pwd = request.POST.get('new_password')
        conf_pwd = request.POST.get('confirm_password')
        pwd_ok = True

        if new_pwd:
            if new_pwd == conf_pwd:
                request.user.set_password(new_pwd)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Mot de passe mis à jour.")
            else:
                messages.error(request, "Les mots de passe ne correspondent pas.")
                pwd_ok = False

        if form.is_valid() and pwd_ok:
            # Force l'enregistrement du nouveau logo (si fourni) AVANT suppression
            instance = form.save()

            # Suppression de l'ancien logo physique si un nouveau est fourni
            if 'logo' in request.FILES and old_has_logo and old_logo_path:
                if os.path.exists(old_logo_path):
                    try:
                        os.remove(old_logo_path)
                    except OSError:
                        pass

            messages.success(request, "Paramètres mis à jour avec succès.")
            return redirect('parametres:index')

    else:
        form = ParametresForm(instance=params)

    return render(request, 'parametres/index.html', {'params': params, 'form': form})


@method_decorator(csrf_exempt, name='dispatch')
class LanguageAPIView(View):
    """API REST pour gérer la langue
    
    GET /api/language/ - Récupère la langue actuelle
    POST /api/language/ - Change la langue (form-data)
    PUT /api/language/ - Change la langue (JSON)
    """
    
    SUPPORTED_LANGUAGES = ['fr', 'en', 'ar']
    
    def get(self, request):
        """GET: Récupérer la langue actuelle"""
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False, 
                'error': 'Authentication required'
            }, status=401)
        
        params, _ = Parametres.objects.get_or_create(pk=1)
        return JsonResponse({
            'success': True,
            'language': params.langue,
            'supported_languages': self.SUPPORTED_LANGUAGES
        })
    
    def post(self, request):
        """POST: Changer la langue avec form-data"""
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)
        
        langue = request.POST.get('language') or request.POST.get('langue')
        
        if not langue:
            return JsonResponse({
                'success': False,
                'error': 'Language parameter required'
            }, status=400)
        
        return self._change_language(langue)
    
    def put(self, request):
        """PUT: Changer la langue avec JSON"""
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Authentication required'
            }, status=401)
        
        try:
            data = json.loads(request.body)
            langue = data.get('language') or data.get('langue')
            
            if not langue:
                return JsonResponse({
                    'success': False,
                    'error': 'Language parameter required'
                }, status=400)
            
            return self._change_language(langue)
        
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON'
            }, status=400)
    
    def _change_language(self, langue):
        """Fonction interne pour changer la langue"""
        if langue not in self.SUPPORTED_LANGUAGES:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported language. Supported: {", ".join(self.SUPPORTED_LANGUAGES)}'
            }, status=400)
        
        params, _ = Parametres.objects.get_or_create(pk=1)
        params.langue = langue
        params.save()
        
        return JsonResponse({
            'success': True,
            'language': langue,
            'message': f'Language changed to {langue}'
        })


@login_required
def api_test(request):
    """Page de test interactif pour l'API de langue"""
    return render(request, 'parametres/api_test.html')
