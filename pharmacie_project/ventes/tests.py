from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from clients.models import Client
from medicaments.models import Medicament, Categorie
from ventes.models import Vente, LigneVente


class VenteModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='caissier', password='Test1234!')
        self.client_obj = Client.objects.create(nom='Diallo', prenom='Fatoumata')
        self.categorie = Categorie.objects.create(nom='Général')
        self.med = Medicament.objects.create(
            nom='Paracetamol', categorie=self.categorie,
            prix_vente=Decimal('500'), prix_achat=Decimal('300'),
            quantite_stock=20, seuil_alerte=5,
        )

    def test_net_a_payer(self):
        vente = Vente(total=Decimal('10000'), remise=Decimal('1500'))
        self.assertEqual(vente.net_a_payer, Decimal('8500'))

    def test_ligne_sous_total(self):
        vente = Vente.objects.create(
            client=self.client_obj, utilisateur=self.user,
            numero_facture='FACT-2026-0001', total=Decimal('1000'),
        )
        ligne = LigneVente(vente=vente, medicament=self.med, quantite=3, prix_unitaire=Decimal('500'))
        ligne.save()
        self.assertEqual(ligne.sous_total, Decimal('1500'))


class NouvelleVenteViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='caissier', password='Test1234!')
        self.client.force_login(self.user)
        self.med = Medicament.objects.create(
            nom='Doliprane', prix_vente=Decimal('1000'), prix_achat=Decimal('600'),
            quantite_stock=10, seuil_alerte=3,
        )

    def test_page_loads(self):
        response = self.client.get(reverse('ventes:nouvelle'))
        self.assertEqual(response.status_code, 200)

    def test_stock_insufficient_blocks_sale(self):
        response = self.client.post(reverse('ventes:nouvelle'), {
            'medicament_id': [str(self.med.pk)],
            'quantite': ['15'],
            'mode_paiement': ['especes'],
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Stock insuffisant')
        self.assertEqual(Medicament.objects.get(pk=self.med.pk).quantite_stock, 10)

    def test_successful_sale_deducts_stock(self):
        response = self.client.post(reverse('ventes:nouvelle'), {
            'medicament_id': [str(self.med.pk)],
            'quantite': ['3'],
            'mode_paiement': ['especes'],
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Medicament.objects.get(pk=self.med.pk).quantite_stock, 7)
        self.assertTrue(Vente.objects.filter(numero_facture__startswith='FACT-').exists())


class AnnulerVenteViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='pharmacien', password='Test1234!', is_staff=True)
        from accounts.models import UserProfile
        UserProfile.objects.create(user=self.user, role=UserProfile.ROLE_PHARMACIEN)
        self.client.force_login(self.user)
        self.med = Medicament.objects.create(
            nom='Ibuprofene', prix_vente=Decimal('800'), prix_achat=Decimal('500'),
            quantite_stock=5, seuil_alerte=2,
        )
        self.vente = Vente.objects.create(
            utilisateur=self.user, numero_facture='FACT-2026-9999',
            total=Decimal('800'), mode_paiement='especes', statut_paiement='paye',
        )
        LigneVente.objects.create(
            vente=self.vente, medicament=self.med, quantite=2, prix_unitaire=Decimal('800'),
        )
        Medicament.objects.filter(pk=self.med.pk).update(quantite_stock=3)

    def test_annuler_restores_stock(self):
        response = self.client.post(
            reverse('ventes:annuler', args=[self.vente.pk]),
            {'motif': 'Test annulation'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.vente.refresh_from_db()
        self.assertEqual(self.vente.statut, 'annulee')
        self.assertEqual(Medicament.objects.get(pk=self.med.pk).quantite_stock, 5)
