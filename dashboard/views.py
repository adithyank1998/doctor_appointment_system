from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.shortcuts import render
from appointments.models import Appointment, Doctor


@login_required
def dashboard(request):
    appointments = Appointment.objects.all()
    if not request.user.is_staff_role:
        appointments = appointments.filter(patient=request.user)
    status_counts = {item['status']: item['count'] for item in appointments.values('status').annotate(count=Count('id'))}
    context = {
        'total_appointments': appointments.count(),
        'confirmed': status_counts.get(Appointment.Status.CONFIRMED, 0),
        'pending': status_counts.get(Appointment.Status.PENDING, 0),
        'completed': status_counts.get(Appointment.Status.COMPLETED, 0),
        'doctor_count': Doctor.objects.filter(is_available=True).count(),
        'recent_appointments': appointments.select_related('doctor', 'patient')[:5],
        'status_counts': status_counts,
    }
    return render(request, 'dashboard/dashboard.html', context)

# Create your views here.
