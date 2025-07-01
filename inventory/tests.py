from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import InventoryItem, InventoryRequest


class EditRequestTestCase(TestCase):
    def setUp(self):
        # Set up initial data and test client
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='admin', password='password123')
        self.user = User.objects.create_user(username='testuser', password='password123')

        # Create an inventory item and request
        self.item = InventoryItem.objects.create(name="Keyboard", description="Mechanical keyboard", quantity=5)
        self.inventory_request = InventoryRequest.objects.create(
            item=self.item,
            requested_by=self.user,
            priority='High',
            status='New'
        )

    def test_edit_request_as_admin(self):
        # Log in as admin
        self.client.login(username='admin', password='password123')

        # Send a POST request to edit the inventory request
        response = self.client.post(
            reverse('edit_request', args=[self.inventory_request.id]),
            {'status': 'Approved'}
        )

        # Assert the response and the redirection
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertRedirects(response, reverse('admin_dashboard'))  # Verify redirect to admin dashboard

        # Fetch the updated request and verify the changes
        updated_request = InventoryRequest.objects.get(id=self.inventory_request.id)
        self.assertEqual(updated_request.status, 'Approved')  # Ensure data is updated correctly

    def test_edit_request_as_non_admin(self):
        # Log in as a non-admin user
        self.client.login(username='testuser', password='password123')

        # Attempt to edit the inventory request
        response = self.client.post(
            reverse('edit_request', args=[self.inventory_request.id]),
            {'status': 'Approved'}
        )

        # Assert that access is forbidden
        self.assertEqual(response.status_code, 403)  # Non-admins shouldn't be allowed to edit requests
