from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import InventoryItem, InventoryRequest


class EditRequestTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='admin', password='password123')
        self.user = User.objects.create_user(username='testuser', password='password123')

        self.item = InventoryItem.objects.create(name="Keyboard", description="Mechanical keyboard", quantity=5)
        self.inventory_request = InventoryRequest.objects.create(
            item=self.item,
            requested_by=self.user,
            priority='High',
            status='New'
        )

    def test_edit_request_as_admin(self):
        self.client.login(username='admin', password='password123')

        response = self.client.post(
            reverse('edit_request', args=[self.inventory_request.id]),
            {'status': 'Approved'}
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('admin_dashboard'))

        updated_request = InventoryRequest.objects.get(id=self.inventory_request.id)
        self.assertEqual(updated_request.status, 'Approved')

    def test_edit_request_as_non_admin(self):
        self.client.login(username='testuser', password='password123')

        response = self.client.post(
            reverse('edit_request', args=[self.inventory_request.id]),
            {'status': 'Approved'}
        )

        self.assertEqual(response.status_code, 403)
