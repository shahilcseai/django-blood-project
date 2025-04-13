from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, DonorProfile, RequesterProfile

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password'
    }))
    
    class Meta:
        model = User
        fields = ['username', 'password']

class DonorRegistrationForm(UserCreationForm):
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    # Donor specific fields
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    blood_group = forms.ChoiceField(choices=BLOOD_GROUPS, widget=forms.Select(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = User.DONOR
        
        if commit:
            user.save()
            donor_profile = DonorProfile(
                user=user,
                phone=self.cleaned_data['phone'],
                date_of_birth=self.cleaned_data['date_of_birth'],
                blood_group=self.cleaned_data['blood_group'],
                address=self.cleaned_data['address']
            )
            donor_profile.save()
        
        return user

class RequesterRegistrationForm(UserCreationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    # Requester specific fields
    organization_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    organization_type = forms.ChoiceField(
        choices=[('hospital', 'Hospital'), ('clinic', 'Clinic'), ('research', 'Research Center'), ('other', 'Other')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    contact_phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = User.REQUESTER
        
        if commit:
            user.save()
            requester_profile = RequesterProfile(
                user=user,
                organization_name=self.cleaned_data['organization_name'],
                organization_type=self.cleaned_data['organization_type'],
                contact_phone=self.cleaned_data['contact_phone'],
                address=self.cleaned_data['address']
            )
            requester_profile.save()
        
        return user

class DonorProfileUpdateForm(forms.ModelForm):
    phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    blood_group = forms.ChoiceField(
        choices=[
            ('A+', 'A+'), ('A-', 'A-'),
            ('B+', 'B+'), ('B-', 'B-'),
            ('AB+', 'AB+'), ('AB-', 'AB-'),
            ('O+', 'O+'), ('O-', 'O-'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    medical_conditions = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    class Meta:
        model = DonorProfile
        fields = ['phone', 'date_of_birth', 'blood_group', 'address', 'medical_conditions']

class RequesterProfileUpdateForm(forms.ModelForm):
    organization_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    organization_type = forms.ChoiceField(
        choices=[('hospital', 'Hospital'), ('clinic', 'Clinic'), ('research', 'Research Center'), ('other', 'Other')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    contact_phone = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    
    class Meta:
        model = RequesterProfile
        fields = ['organization_name', 'organization_type', 'contact_phone', 'address']

class UserInfoUpdateForm(forms.ModelForm):
    first_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
