from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from accounts.decorators import staff_required
from .forms import AppointmentForm, AppointmentStatusForm, DoctorForm, PrescriptionForm, PatientProfileForm
from .models import Appointment, Doctor, Prescription, PatientProfile


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
            messages.error(request, 'This doctor has appointments and cannot be deleted.')
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


@login_required
def appointment_detail(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)
    is_assigned_doctor = (
        request.user.is_doctor_role and
        hasattr(request.user, 'doctor_profile') and
        request.user.doctor_profile == appointment.doctor
    )
    if not (appointment.patient == request.user or request.user.is_staff_role or is_assigned_doctor):
        messages.error(request, 'Access denied.')
        return redirect('appointment_list')
    profile = PatientProfile.objects.filter(patient=appointment.patient).first()
    prescription = Prescription.objects.filter(appointment=appointment).first()
    return render(request, 'appointments/appointment_detail.html', {
        'appointment': appointment,
        'profile': profile,
        'prescription': prescription,
    })


@login_required
def prescription_create(request, appointment_pk):
    appointment = get_object_or_404(Appointment, pk=appointment_pk)
    is_assigned_doctor = (
        request.user.is_doctor_role and
        hasattr(request.user, 'doctor_profile') and
        request.user.doctor_profile == appointment.doctor
    )
    if not is_assigned_doctor:
        messages.error(request, 'Only the assigned doctor can write a prescription.')
        return redirect('appointment_detail', pk=appointment_pk)
    if hasattr(appointment, 'prescription'):
        return redirect('prescription_edit', pk=appointment.prescription.pk)
    form = PrescriptionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        prescription = form.save(commit=False)
        prescription.appointment = appointment
        prescription.doctor = appointment.doctor
        prescription.patient = appointment.patient
        prescription.save()
        appointment.status = Appointment.Status.COMPLETED
        appointment.save()
        messages.success(request, 'Prescription saved and sent to patient.')
        return redirect('appointment_detail', pk=appointment_pk)
    return render(request, 'form.html', {'form': form, 'title': 'Write prescription'})


@login_required
def prescription_edit(request, pk):
    prescription = get_object_or_404(Prescription, pk=pk)
    is_assigned_doctor = (
        request.user.is_doctor_role and
        hasattr(request.user, 'doctor_profile') and
        request.user.doctor_profile == prescription.doctor
    )
    if not is_assigned_doctor:
        messages.error(request, 'Access denied.')
        return redirect('doctor_dashboard')
    form = PrescriptionForm(request.POST or None, instance=prescription)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Prescription updated.')
        return redirect('appointment_detail', pk=prescription.appointment.pk)
    return render(request, 'form.html', {'form': form, 'title': 'Edit prescription'})


@login_required
def my_prescriptions(request):
    prescriptions = Prescription.objects.filter(patient=request.user).select_related('doctor', 'appointment')
    return render(request, 'appointments/my_prescriptions.html', {'prescriptions': prescriptions})


@login_required
def patient_profile(request):
    profile, created = PatientProfile.objects.get_or_create(patient=request.user)
    form = PatientProfileForm(request.POST or None, instance=profile)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated.')
        return redirect('patient_profile')
    return render(request, 'appointments/patient_profile.html', {'form': form})


@login_required
def patient_detail(request, pk):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    patient = get_object_or_404(User, pk=pk)
    is_assigned_doctor = (
        request.user.is_doctor_role and
        hasattr(request.user, 'doctor_profile') and
        Appointment.objects.filter(
            doctor=request.user.doctor_profile,
            patient=patient
        ).exists()
    )
    if not (request.user.is_staff_role or is_assigned_doctor):
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    profile = PatientProfile.objects.filter(patient=patient).first()
    appointments = Appointment.objects.filter(patient=patient).select_related('doctor')
    prescriptions = Prescription.objects.filter(patient=patient).select_related('doctor')
    return render(request, 'appointments/patient_detail.html', {
        'patient': patient,
        'profile': profile,
        'appointments': appointments,
        'prescriptions': prescriptions,
    })


@login_required
def doctor_dashboard(request):
    if not request.user.is_doctor_role:
        messages.error(request, 'Access denied.')
        return redirect('dashboard')
    doctor = get_object_or_404(Doctor, user=request.user)
    appointments = Appointment.objects.filter(doctor=doctor).select_related('patient', 'patient__patient_profile')

    status_filter = request.GET.get('status', '')
    if status_filter:
        appointments = appointments.filter(status=status_filter)

    counts = Appointment.objects.filter(doctor=doctor).values('status').annotate(count=Count('id'))
    status_counts = {item['status']: item['count'] for item in counts}

    recent_prescriptions = Prescription.objects.filter(
        doctor=doctor
    ).select_related('patient', 'appointment').order_by('-created_at')[:5]

    return render(request, 'appointments/doctor_dashboard.html', {
        'doctor': doctor,
        'appointments': appointments,
        'status_filter': status_filter,
        'total': sum(item['count'] for item in counts),
        'pending': status_counts.get('PENDING', 0),
        'confirmed': status_counts.get('CONFIRMED', 0),
        'completed': status_counts.get('COMPLETED', 0),
        'recent_prescriptions': recent_prescriptions,
    })