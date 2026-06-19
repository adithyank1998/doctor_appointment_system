from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import staff_required
from .forms import AppointmentForm, AppointmentStatusForm, DoctorForm
from .models import Appointment, Doctor


def doctor_list(request):
    query = request.GET.get('q', '').strip()
    doctors = Doctor.objects.all()
    if query:
        doctors = doctors.filter(Q(name__icontains=query) | Q(specialization__icontains=query))
    return render(request, 'appointments/doctor_list.html', {'doctors': doctors, 'query': query})


@login_required
@staff_required
def doctor_create(request):
    return _doctor_form(request, DoctorForm(request.POST or None), 'Add doctor')


@login_required
@staff_required
def doctor_update(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    return _doctor_form(request, DoctorForm(request.POST or None, instance=doctor), 'Edit doctor')


def _doctor_form(request, form, title):
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Doctor saved.')
        return redirect('doctor_list')
    return render(request, 'form.html', {'form': form, 'title': title})


@login_required
@staff_required
def doctor_delete(request, pk):
    doctor = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        try:
            doctor.delete()
            messages.success(request, 'Doctor deleted.')
        except Exception:
            messages.error(request, 'This doctor has appointments and cannot be deleted. Mark them unavailable instead.')
        return redirect('doctor_list')
    return render(request, 'confirm_delete.html', {'object': doctor})


@login_required
def appointment_list(request):
    appointments = Appointment.objects.select_related('doctor', 'patient')
    if not request.user.is_staff_role:
        appointments = appointments.filter(patient=request.user)
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})


@login_required
def appointment_create(request):
    form = AppointmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        appointment = form.save(commit=False)
        appointment.patient = request.user
        try:
            appointment.save()
            messages.success(request, 'Appointment request submitted.')
            return redirect('appointment_list')
        except IntegrityError:
            form.add_error(None, 'That time slot has already been booked.')
    return render(request, 'form.html', {'form': form, 'title': 'Book appointment'})


@login_required
def appointment_update(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.patient != request.user and not request.user.is_staff_role:
        messages.error(request, 'You may only edit your own appointments.')
        return redirect('appointment_list')
    form_class = AppointmentStatusForm if request.user.is_staff_role else AppointmentForm
    form = form_class(request.POST or None, instance=appointment)
    if request.method == 'POST' and form.is_valid():
        try:
            form.save()
            messages.success(request, 'Appointment updated.')
            return redirect('appointment_list')
        except IntegrityError:
            form.add_error(None, 'That time slot has already been booked.')
    return render(request, 'form.html', {'form': form, 'title': 'Update appointment'})


@login_required
def appointment_delete(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    if appointment.patient != request.user and not request.user.is_admin_role:
        messages.error(request, 'You may only delete your own appointments.')
        return redirect('appointment_list')
    if request.method == 'POST':
        appointment.delete()
        messages.success(request, 'Appointment deleted.')
        return redirect('appointment_list')
    return render(request, 'confirm_delete.html', {'object': appointment})

# Create your views here.
