from django.urls import path
from . import views

urlpatterns = [
    path('doctors/', views.doctor_list, name='doctor_list'),
    path('doctors/add/', views.doctor_create, name='doctor_create'),
    path('doctors/<int:pk>/edit/', views.doctor_update, name='doctor_update'),
    path('doctors/<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    path('', views.appointment_list, name='appointment_list'),
    path('book/', views.appointment_create, name='appointment_create'),
    path('<int:pk>/edit/', views.appointment_update, name='appointment_update'),
    path('<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
]
