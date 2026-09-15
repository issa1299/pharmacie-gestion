import secrets
import uuid


def _generer_secret_webhook():
    """Secret unique par vente — sert à signer les appels webhook (HMAC)."""
    return secrets.token_hex(32)


def initier_paiement(vente):
    """
    Simule l'initialisation d'un paiement avec un agrégateur.
    Retourne l'URL de paiement ou les informations nécessaires.
    """
    # 1. Générer une référence de transaction unique + secret HMAC
    transaction_id = str(uuid.uuid4())
    vente.reference_paiement = transaction_id
    vente.secret_webhook = _generer_secret_webhook()
    vente.statut_paiement = 'en_attente'
    vente.save(update_fields=['reference_paiement', 'secret_webhook', 'statut_paiement'])

    # 2. Préparer les données pour l'API (montant, devise, ref, etc.)
    # montant = vente.total - vente.remise
    # payload = {
    #     "apikey": API_KEY,
    #     "site_id": SITE_ID,
    #     "transaction_id": transaction_id,
    #     "amount": int(montant),
    #     "currency": "XOF",
    #     "description": f"Paiement facture {vente.numero_facture}",
    #     "return_url": f"https://votre-site.com/ventes/{vente.id}/",
    #     "notify_url": "https://votre-site.com/ventes/webhook/",
    #     "channels": "ALL"
    # }
    
    # 3. Appel à l'API (Simulation)
    # response = requests.post("https://api-sandbox.fournisseur.com/v1/payment", json=payload)
    # data = response.json()
    # payment_url = data.get("payment_url")
    
    from django.urls import reverse
    # Pour le moment on simule l'URL
    payment_url = f"{reverse('ventes:mock_payment', args=[vente.id])}?ref={transaction_id}"
    
    return payment_url

def verifier_statut_paiement(reference_paiement):
    """
    Simule la vérification du statut d'un paiement auprès de l'agrégateur.
    Normalement utilisé en backup du webhook.
    """
    # payload = {"apikey": API_KEY, "site_id": SITE_ID, "transaction_id": reference_paiement}
    # response = requests.post("https://api-sandbox.fournisseur.com/v1/check", json=payload)
    # return response.json().get('status')
    
    pass
