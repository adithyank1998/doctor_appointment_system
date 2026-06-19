from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import get_object_or_404, redirect, render
from .decorators import admin_required
from .forms import SignupForm, UserRoleForm
from .models import User


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
    users = User.objects.order_by('username')
    return render(request, 'accounts/user_list.html', {'users': users})


@login_required
@admin_required
def user_update(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserRoleForm(request.POST or None, instance=user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'User updated.')
        return redirect('user_list')
    return render(request, 'form.html', {'form': form, 'title': 'Edit user'})

# Create your views here.
