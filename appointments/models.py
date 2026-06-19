from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Doctor(models.Model):
    name = models.CharField(max_length=120)
    specialization = models.CharField(max_length=120)
    qualification = models.CharField(max_length=160, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    consultation_fee = models.DecimalField(max_digits=8, decimal_places=2)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return f'Dr. {self.name} - {self.specialization}'


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    patient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    reason = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-appointment_date', '-appointment_time')
        constraints = [models.UniqueConstraint(fields=('doctor', 'appointment_date', 'appointment_time'), name='unique_doctor_slot')]

    def clean(self):
        if self.appointment_date and self.appointment_date < timezone.localdate():
            raise ValidationError({'appointment_date': 'Appointments cannot be booked in the past.'})

    def __str__(self):
        return f'{self.patient} with {self.doctor} on {self.appointment_date}'

# Create your models here.
