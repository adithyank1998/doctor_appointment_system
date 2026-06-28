from django import forms
from django.db.models import Q
from .models import Appointment, Doctor, Prescription, PatientProfile


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


class DoctorForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = '__all__'


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('doctor', 'appointment_date', 'appointment_time', 'reason')
        widgets = {
            'appointment_date': DateInput(),
            'appointment_time': TimeInput(),
            'reason': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current = self.instance.doctor_id if self.instance and self.instance.pk else None
        self.fields['doctor'].queryset = Doctor.objects.filter(Q(is_available=True) | Q(pk=current))


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('status',)


class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        fields = ('medicines', 'notes', 'next_visit_date')
        widgets = {
            'medicines': forms.Textarea(attrs={'rows': 4, 'placeholder': 'e.g. Paracetamol 500mg - 1 tablet twice daily'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Additional instructions for the patient'}),
            'next_visit_date': DateInput(),
        }


class PatientProfileForm(forms.ModelForm):
    class Meta:
        model = PatientProfile
        fields = (
            'age', 'height_cm', 'weight_kg', 'blood_group',
            'medical_history', 'current_medications', 'allergies',
            'emergency_contact_name', 'emergency_contact_phone',
        )
        widgets = {
            'medical_history': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Past illnesses, surgeries, chronic conditions...'}),
            'current_medications': forms.Textarea(attrs={'rows': 2, 'placeholder': 'List any medications you are currently taking'}),
            'allergies': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Food, drug, or environmental allergies'}),
        }

from .models import Appointment, Doctor, Prescription, PatientProfile, DoctorAvailability


class DoctorProfileForm(forms.ModelForm):
    class Meta:
        model = Doctor
        fields = ('name', 'specialization', 'qualification', 'experience_years', 'consultation_fee', 'bio', 'is_available')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class DoctorAvailabilityForm(forms.ModelForm):
    class Meta:
        model = DoctorAvailability
        fields = ('day', 'start_time', 'end_time')
        widgets = {
            'start_time': TimeInput(),
            'end_time': TimeInput(),
        }