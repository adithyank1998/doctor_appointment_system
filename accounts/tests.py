from django.test import TestCase
from django.urls import reverse
from .models import User


class AccountTests(TestCase):
    def test_signup_always_creates_patient(self):
        response = self.client.post(reverse('signup'), {'username': 'newpatient', 'email': 'new@example.com', 'password1': 'StrongPass!234', 'password2': 'StrongPass!234'})
        self.assertRedirects(response, reverse('login'))
        self.assertEqual(User.objects.get(username='newpatient').role, User.Role.PATIENT)

    def test_patient_cannot_manage_users(self):
        patient = User.objects.create_user('patient', password='testpass', role=User.Role.PATIENT)
        self.client.force_login(patient)
        self.assertRedirects(self.client.get(reverse('user_list')), reverse('dashboard'))

    def test_admin_can_manage_users(self):
        admin = User.objects.create_user('admin', password='testpass', role=User.Role.ADMIN)
        self.client.force_login(admin)
        self.assertEqual(self.client.get(reverse('user_list')).status_code, 200)

# Create your tests here.
