from datetime import date, time, timedelta
from django.test import TestCase
from django.urls import reverse
from accounts.models import User
from .models import Appointment, Doctor


class AppointmentPermissionTests(TestCase):
    def setUp(self):
        self.patient = User.objects.create_user('patient', password='testpass', role=User.Role.PATIENT)
        self.other = User.objects.create_user('other', password='testpass', role=User.Role.PATIENT)
        self.staff = User.objects.create_user('staff', password='testpass', role=User.Role.STAFF)
        self.doctor = Doctor.objects.create(name='A Doctor', specialization='General', consultation_fee=500)
        self.appointment = Appointment.objects.create(patient=self.patient, doctor=self.doctor, appointment_date=date.today() + timedelta(days=1), appointment_time=time(9), reason='Checkup')

    def test_patient_can_book(self):
        self.client.force_login(self.patient)
        response = self.client.post(reverse('appointment_create'), {'doctor': self.doctor.pk, 'appointment_date': date.today() + timedelta(days=2), 'appointment_time': '10:00', 'reason': 'Follow-up'})
        self.assertRedirects(response, reverse('appointment_list'))
        self.assertEqual(Appointment.objects.count(), 2)

    def test_patient_cannot_edit_another_patients_appointment(self):
        self.client.force_login(self.other)
        self.assertRedirects(self.client.get(reverse('appointment_update', args=[self.appointment.pk])), reverse('appointment_list'))

    def test_patient_cannot_manage_doctors(self):
        self.client.force_login(self.patient)
        self.assertRedirects(self.client.get(reverse('doctor_create')), reverse('dashboard'))

    def test_staff_can_manage_doctors_and_status(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(reverse('doctor_update', args=[self.doctor.pk])).status_code, 200)
        response = self.client.post(reverse('appointment_update', args=[self.appointment.pk]), {'status': Appointment.Status.CONFIRMED})
        self.assertRedirects(response, reverse('appointment_list'))
        self.appointment.refresh_from_db()
        self.assertEqual(self.appointment.status, Appointment.Status.CONFIRMED)

    def test_duplicate_doctor_slot_is_rejected(self):
        self.client.force_login(self.other)
        response = self.client.post(reverse('appointment_create'), {'doctor': self.doctor.pk, 'appointment_date': self.appointment.appointment_date, 'appointment_time': '09:00', 'reason': 'Consultation'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Appointment.objects.count(), 1)

    def test_protected_page_redirects_anonymous_user(self):
        response = self.client.get(reverse('appointment_list'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('appointment_list')}")

# Create your tests here.
