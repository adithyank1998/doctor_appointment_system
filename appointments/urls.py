from django.urls import path
from . import views

urlpatterns = [
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/add/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/edit/', views.doctor_update, name='doctor_update'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    path('', views.appointment_list, name='appointment_list'),
    path('book/', views.appointment_create, name='appointment_create'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/edit/', views.appointment_update, name='appointment_update'),
    path('<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
    path('<int:appointment_pk>/prescription/add/', views.prescription_create, name='prescription_create'),
    path('prescription/<int:pk>/edit/', views.prescription_edit, name='prescription_edit'),
    path('my-prescriptions/', views.my_prescriptions, name='my_prescriptions'),
    path('profile/', views.patient_profile, name='patient_profile'),
    path('patient/<int:pk>/', views.patient_detail, name='patient_detail'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('doctor-profile/edit/', views.doctor_profile_edit, name='doctor_profile_edit'),
    path('doctor-availability/', views.doctor_availability, name='doctor_availability'),
    path('doctor-availability/<int:pk>/delete/', views.doctor_availability_delete, name='doctor_availability_delete'),
]