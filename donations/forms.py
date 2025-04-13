from django import forms
from .models import Appointment, Donation
from datetime import datetime, timedelta

class AppointmentForm(forms.ModelForm):
    # Ensure appointment dates are in the future and only within next 30 days
    appointment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local',
            'min': datetime.now().strftime('%Y-%m-%dT%H:%M'),
            'max': (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M')
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requirements or medical conditions we should know about?'
        })
    )
    
    class Meta:
        model = Appointment
        fields = ['appointment_date', 'notes']
    
    def clean_appointment_date(self):
        appointment_date = self.cleaned_data.get('appointment_date')
        
        # Use Django's timezone utilities to ensure both dates are timezone-aware
        from django.utils import timezone
        now = timezone.now()
        
        if appointment_date < now:
            raise forms.ValidationError("Appointment date cannot be in the past.")
        
        max_date = now + timedelta(days=30)
        if appointment_date > max_date:
            raise forms.ValidationError("Appointment cannot be scheduled more than 30 days in advance.")
        
        return appointment_date

class DonationForm(forms.ModelForm):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    blood_group = forms.ChoiceField(
        choices=BLOOD_GROUPS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    units = forms.IntegerField(
        min_value=1,
        max_value=3,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    donation_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    hemoglobin_level = forms.FloatField(
        required=False,
        min_value=8.0,
        max_value=20.0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.1'
        })
    )
    
    pulse_rate = forms.IntegerField(
        required=False,
        min_value=50,
        max_value=120,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    blood_pressure = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., 120/80'
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3
        })
    )
    
    class Meta:
        model = Donation
        fields = ['blood_group', 'units', 'donation_date', 'hemoglobin_level', 
                 'pulse_rate', 'blood_pressure', 'notes']
    
    def clean_donation_date(self):
        donation_date = self.cleaned_data.get('donation_date')
        
        # Use Django's timezone utilities for consistency
        from django.utils import timezone
        now = timezone.now().date()
        
        if donation_date > now:
            raise forms.ValidationError("Donation date cannot be in the future.")
        
        return donation_date
