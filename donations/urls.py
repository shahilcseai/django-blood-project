from django.urls import path
from . import views

urlpatterns = [
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.create_appointment, name='create_appointment'),
    path('appointments/<int:pk>/cancel/', views.cancel_appointment, name='cancel_appointment'),
    path('appointments/<int:pk>/complete/', views.complete_appointment, name='complete_appointment'),
    path('history/', views.donation_history, name='donation_history'),
    path('record/', views.record_donation, name='record_donation'),
    path('export/history/', views.export_donation_history, name='export_donation_history'),
]
