from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.ClinicLoginView.as_view(), name='login'),
    path('logout/', views.ClinicLogoutView.as_view(), name='logout'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/edit/', views.user_update, name='user_update'),
]
