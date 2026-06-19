from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect


def role_required(check):
    def decorator(view):
        @wraps(view)
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated and check(request.user):
                return view(request, *args, **kwargs)
            messages.error(request, 'You do not have permission to access that page.')
            return redirect('dashboard')
        return wrapped
    return decorator


staff_required = role_required(lambda user: user.is_staff_role)
admin_required = role_required(lambda user: user.is_admin_role)
