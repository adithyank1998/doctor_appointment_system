from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import redirect, render
from appointments.models import Appointment, Doctor, Prescription, PatientProfile


@login_required
def dashboard(request):
    user = request.user

    # Doctor role — redirect to doctor dashboard
    if user.is_doctor_role:
        return redirect('doctor_dashboard')

    appointments = Appointment.objects.all()
    if not user.is_staff_role:
        appointments = appointments.filter(patient=user)

    status_counts = {
        item['status']: item['count']
        for item in appointments.values('status').annotate(count=Count('id'))
    }

    # Extra context for patients
    prescriptions = []
    patient_profile = None
    if user.is_patient_role:
        prescriptions = Prescription.objects.filter(patient=user).select_related('doctor')[:3]
        patient_profile = PatientProfile.objects.filter(patient=user).first()

    context = {
        'total_appointments': appointments.count(),
        'confirmed': status_counts.get(Appointment.Status.CONFIRMED, 0),
        'pending': status_counts.get(Appointment.Status.PENDING, 0),
        'completed': status_counts.get(Appointment.Status.COMPLETED, 0),
        'doctor_count': Doctor.objects.filter(is_available=True).count(),
        'recent_appointments': appointments.select_related('doctor', 'patient')[:5],
        'status_counts': status_counts,
        'prescriptions': prescriptions,
        'patient_profile': patient_profile,
    }
    return render(request, 'dashboard/dashboard.html', context)