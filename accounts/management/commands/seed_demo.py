from datetime import date, time, timedelta
from decimal import Decimal
from django.core.management.base import BaseCommand
from accounts.models import User
from appointments.models import Appointment, Doctor


class Command(BaseCommand):
    help = 'Create demonstration users, doctors, and appointments.'

    def handle(self, *args, **options):
        users = [
            ('admin', 'Admin@12345', User.Role.ADMIN, True, True),
            ('staff', 'Staff@12345', User.Role.STAFF, True, False),
            ('patient', 'Patient@12345', User.Role.PATIENT, False, False),
        ]
        created_users = {}
        for username, password, role, is_staff, is_superuser in users:
            user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@carepoint.test', 'role': role, 'is_staff': is_staff, 'is_superuser': is_superuser})
            user.role, user.is_staff, user.is_superuser = role, is_staff, is_superuser
            if created or not user.has_usable_password():
                user.set_password(password)
            user.save()
            created_users[username] = user
        doctors = [('Ananya Rao', 'Cardiology', 'MD, DM Cardiology', 12, '850.00'), ('Vikram Shah', 'Dermatology', 'MD Dermatology', 9, '650.00'), ('Meera Nair', 'Pediatrics', 'MD Pediatrics', 15, '700.00')]
        doctor_objects = []
        for name, specialty, qualification, years, fee in doctors:
            doctor, _ = Doctor.objects.get_or_create(name=name, defaults={'specialization': specialty, 'qualification': qualification, 'experience_years': years, 'consultation_fee': Decimal(fee), 'bio': f'Experienced {specialty.lower()} specialist focused on clear, compassionate care.'})
            doctor_objects.append(doctor)
        Appointment.objects.get_or_create(patient=created_users['patient'], doctor=doctor_objects[0], appointment_date=date.today() + timedelta(days=3), appointment_time=time(10, 30), defaults={'reason': 'Routine consultation'})
        self.stdout.write(self.style.SUCCESS('Demo data ready. See README.md for login credentials.'))
