from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import admin_required
from .forms import SignupForm, UserRoleForm, AdminUserCreateForm
from .models import User
from appointments.models import Doctor, Appointment, PatientProfile, Prescription


def home(request):
    return render(request, 'home.html')


def signup(request):
    form = SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Account created. You can now sign in.')
        return redirect('login')
    return render(request, 'registration/signup.html', {'form': form})


class ClinicLoginView(LoginView):
    template_name = 'registration/login.html'


class ClinicLogoutView(LogoutView):
    pass


@login_required
@admin_required
def user_list(request):
    role_filter = request.GET.get('role', '')
    users = User.objects.order_by('role', 'username')
    if role_filter:
        users = users.filter(role=role_filter)
    return render(request, 'accounts/user_list.html', {
        'users': users,
        'role_filter': role_filter,
        'roles': User.Role.choices,
    })


@login_required
@admin_required
def user_create(request):
    form = AdminUserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        if user.role == User.Role.DOCTOR:
            Doctor.objects.create(
                user=user,
                name=f'{user.first_name} {user.last_name}'.strip() or user.username,
                specialization='General',
                consultation_fee=0,
            )
            messages.success(request, f'Doctor account created. Please update their doctor profile.')
        else:
            messages.success(request, f'User {user.username} created successfully.')
        return redirect('user_list')
    return render(request, 'form.html', {'form': form, 'title': 'Create new user'})


@login_required
@admin_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserRoleForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated.')
        return redirect('user_list')
    return render(request, 'form.html', {'form': form, 'title': f'Edit user — {user.username}'})


@login_required
@admin_required
def user_detail(request, pk):
    patient = get_object_or_404(User, pk=pk)
    profile = PatientProfile.objects.filter(patient=patient).first()
    appointments = []
    prescriptions = []
    doctor_profile = None
    if patient.role == User.Role.PATIENT:
        appointments = Appointment.objects.filter(patient=patient).select_related('doctor')
        prescriptions = Prescription.objects.filter(patient=patient).select_related('doctor')
    if patient.role == User.Role.DOCTOR:
        doctor_profile = Doctor.objects.filter(user=patient).first()
    return render(request, 'accounts/user_detail.html', {
        'patient': patient,
        'profile': profile,
        'appointments': appointments,
        'prescriptions': prescriptions,
        'doctor_profile': doctor_profile,
    })