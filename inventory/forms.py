from django import forms
from .models import BloodInventory, InventoryLog

class InventoryForm(forms.ModelForm):
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
    
    units_available = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = BloodInventory
        fields = ['blood_group', 'units_available']

class InventoryUpdateForm(forms.Form):
    ACTIONS = [
        ('add', 'Add Units'),
        ('remove', 'Remove Units'),
        ('adjust', 'Adjust to Exact Amount')
    ]
    
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
    
    action = forms.ChoiceField(
        choices=ACTIONS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    units = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Reason for adjustment'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        action = cleaned_data.get('action')
        units = cleaned_data.get('units')
        blood_group = cleaned_data.get('blood_group')
        
        if action == 'remove':
            # Check if there are enough units to remove
            inventory = BloodInventory.objects.filter(blood_group=blood_group).first()
            if inventory and inventory.units_available < units:
                self.add_error('units', f"Not enough units available. Current inventory: {inventory.units_available}")
        
        return cleaned_data
