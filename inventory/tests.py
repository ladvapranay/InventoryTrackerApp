from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse

from .models import InventoryItem, InventoryRequest


class InventoryAppTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="regularuser",
            password="Testpass123!"
        )

        self.other_user = User.objects.create_user(
            username="otheruser",
            password="Testpass123!"
        )

        self.admin = User.objects.create_user(
            username="adminuser",
            password="Testpass123!",
            is_staff=True
        )

        self.item = InventoryItem.objects.create(
            name="Laptop",
            quantity=5,
            location="London"
        )

        self.inventory_request = InventoryRequest.objects.create(
            item=self.item,
            reason="Need a laptop for project delivery",
            priority="Medium",
            requested_by=self.user,
            status="New"
        )

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_logged_in_user_can_view_dashboard(self):
        self.client.login(username="regularuser", password="Testpass123!")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_user_cannot_edit_another_users_request(self):
        self.client.login(username="otheruser", password="Testpass123!")
        response = self.client.get(reverse("edit_request", args=[self.inventory_request.id]))
        self.assertEqual(response.status_code, 403)

    def test_user_cannot_delete_request(self):
        self.client.login(username="regularuser", password="Testpass123!")
        response = self.client.get(reverse("delete_request", args=[self.inventory_request.id]))
        self.assertEqual(response.status_code, 403)

    def test_admin_can_open_delete_confirmation_page(self):
        self.client.login(username="adminuser", password="Testpass123!")
        response = self.client.get(reverse("delete_request", args=[self.inventory_request.id]))
        self.assertEqual(response.status_code, 200)

    def test_create_request_successfully(self):
        self.client.login(username="regularuser", password="Testpass123!")
        response = self.client.post(reverse("create_request"), {
            "item": "Laptop",
            "reason": "Need laptop for development work",
            "priority": "High"
        })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(InventoryRequest.objects.count(), 2)

    def test_weak_password_rejected_on_register(self):
        response = self.client.post(reverse("register"), {
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "123",
            "confirm_password": "123"
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="weakuser").exists())

    def test_mismatched_passwords_rejected_on_register(self):
        response = self.client.post(reverse("register"), {
            "username": "mismatchuser",
            "email": "mismatch@example.com",
            "password": "Testpass123!",
            "confirm_password": "Different123!"
        })

        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(username="mismatchuser").exists())

