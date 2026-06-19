from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        STAFF = 'STAFF', 'Staff'
        PATIENT = 'PATIENT', 'Patient'

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.PATIENT)
    phone = models.CharField(max_length=20, blank=True)

    @property
    def is_admin_role(self):
        return self.is_superuser or self.role == self.Role.ADMIN

    @property
    def is_staff_role(self):
        return self.is_admin_role or self.role == self.Role.STAFF

# Create your models here.
