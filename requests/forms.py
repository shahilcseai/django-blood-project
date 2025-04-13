from django import forms
from django.utils import timezone
from datetime import timedelta
from .models import BloodRequest

class BloodRequestForm(forms.ModelForm):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low - Within Weeks'),
        ('medium', 'Medium - Within Days'),
        ('high', 'High - Within 24 Hours'),
        ('critical', 'Critical - Immediately')
    ]
    
    blood_group = forms.ChoiceField(
        choices=BLOOD_GROUPS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    units_needed = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    priority = forms.ChoiceField(
        choices=PRIORITY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    needed_by = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'min': timezone.now().date().isoformat(),
            'max': (timezone.now().date() + timedelta(days=90)).isoformat()
        })
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please provide any relevant information about this request'
        })
    )
    
    patient_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Patient name (optional)'
        })
    )
    
    class Meta:
        model = BloodRequest
        fields = ['blood_group', 'units_needed', 'priority', 'needed_by', 'notes', 'patient_name']
    
    def clean(self):
        cleaned_data = super().clean()
        priority = cleaned_data.get('priority')
        needed_by = cleaned_data.get('needed_by')
        
        # If priority is critical or high, needed_by should be soon
        if priority in ['critical', 'high'] and needed_by:
            max_days = 1 if priority == 'critical' else 3
            max_date = timezone.now().date() + timedelta(days=max_days)
            
            if needed_by > max_date:
                raise forms.ValidationError(
                    f"For {priority} priority, the 'needed by' date should be within {max_days} days."
                )
        
        # For any priority, make sure needed_by is set if not critical
        if priority != 'critical' and not needed_by:
            raise forms.ValidationError("Please specify when the blood is needed by.")
        
        return cleaned_data

class RequestResponseForm(forms.Form):
    """Form for responding to blood requests"""
    STATUS_CHOICES = [
        ('pending', 'Keep Pending'),
        ('processing', 'Mark as Processing'),
        ('fulfilled', 'Mark as Fulfilled'),
        ('rejected', 'Reject Request')
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    rejected_reason = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Reason for rejection (required if rejecting)'
        })
    )
    
    admin_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Internal notes (not visible to requester)'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        rejected_reason = cleaned_data.get('rejected_reason')
        
        if status == 'rejected' and not rejected_reason:
            raise forms.ValidationError("Please provide a reason for rejection.")
        
        return cleaned_data
