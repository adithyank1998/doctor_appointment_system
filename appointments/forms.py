from django import forms
from django.db.models import Q
from .models import Appointment, Doctor


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
        widgets = {'appointment_date': DateInput(), 'appointment_time': TimeInput(), 'reason': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        current = self.instance.doctor_id if self.instance and self.instance.pk else None
        self.fields['doctor'].queryset = Doctor.objects.filter(Q(is_available=True) | Q(pk=current))


class AppointmentStatusForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ('status',)
