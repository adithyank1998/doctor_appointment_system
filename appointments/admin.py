from django.contrib import admin
from .models import Appointment, Doctor


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialization', 'consultation_fee', 'is_available')
    list_filter = ('specialization', 'is_available')
    search_fields = ('name', 'specialization')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status')
    list_filter = ('status', 'appointment_date')
    search_fields = ('patient__username', 'doctor__name')

# Register your models here.
