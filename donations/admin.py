from django.contrib import admin
from .models import Appointment, Donation

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('donor', 'appointment_date', 'status', 'created_at')
    list_filter = ('status', 'appointment_date')
    search_fields = ('donor__username', 'donor__first_name', 'donor__last_name')
    date_hierarchy = 'appointment_date'

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ('donor', 'donation_date', 'blood_group', 'units', 'status')
    list_filter = ('status', 'donation_date', 'blood_group')
    search_fields = ('donor__username', 'donor__first_name', 'donor__last_name')
    date_hierarchy = 'donation_date'
