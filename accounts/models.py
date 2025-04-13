from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    # User type choices
    DONOR = 'donor'
    REQUESTER = 'requester'
    ADMIN = 'admin'
    
    USER_TYPE_CHOICES = [
        (DONOR, 'Donor'),
        (REQUESTER, 'Requester'),
        (ADMIN, 'Admin'),
    ]
    
    user_type = models.CharField(
        _('User Type'),
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default=DONOR,
    )
    
    def is_donor(self):
        return self.user_type == self.DONOR
    
    def is_requester(self):
        return self.user_type == self.REQUESTER
    
    def is_admin_user(self):
        return self.user_type == self.ADMIN
    
    def get_user_type_display(self):
        """Return user-friendly display of user type"""
        for value, display in self.USER_TYPE_CHOICES:
            if value == self.user_type:
                return display
        return self.user_type
        
    def __str__(self):
        return self.username

class DonorProfile(models.Model):
    # Blood group choices
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='donor_profile'
    )
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    address = models.TextField()
    medical_conditions = models.TextField(blank=True, null=True)
    last_donation_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username}'s Donor Profile"
    
    @property
    def donation_count(self):
        return self.user.donations.count()

class RequesterProfile(models.Model):
    # Organization type choices
    ORGANIZATION_TYPES = [
        ('hospital', 'Hospital'),
        ('clinic', 'Clinic'),
        ('research', 'Research Center'),
        ('other', 'Other'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='requester_profile'
    )
    organization_name = models.CharField(max_length=100)
    organization_type = models.CharField(max_length=20, choices=ORGANIZATION_TYPES)
    contact_phone = models.CharField(max_length=20)
    address = models.TextField()
    verified = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.organization_name} ({self.user.username})"
    
    @property
    def request_count(self):
        return self.user.blood_requests.count()
        
    def get_organization_type_display(self):
        """Return user-friendly display of organization type"""
        for value, display in self.ORGANIZATION_TYPES:
            if value == self.organization_type:
                return display
        return self.organization_type
