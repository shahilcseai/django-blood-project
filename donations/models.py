from django.db import models
from django.conf import settings
from django.utils import timezone

class Appointment(models.Model):
    """
    Model to track blood donation appointments.
    """
    # Status choices for appointments
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (CONFIRMED, 'Confirmed'),
        (COMPLETED, 'Completed'),
        (CANCELLED, 'Cancelled'),
        (NO_SHOW, 'No Show'),
    ]
    
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    appointment_date = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-appointment_date']
    
    def __str__(self):
        return f"{self.donor.username} - {self.appointment_date.strftime('%Y-%m-%d %H:%M')} ({self.get_status_display()})"
    
    def is_upcoming(self):
        return self.appointment_date > timezone.now() and self.status not in [self.COMPLETED, self.CANCELLED, self.NO_SHOW]
    
    def is_past_due(self):
        return self.appointment_date < timezone.now() and self.status == self.PENDING
    
    def cancel(self):
        self.status = self.CANCELLED
        self.save()
    
    def confirm(self):
        self.status = self.CONFIRMED
        self.save()
    
    def complete(self):
        self.status = self.COMPLETED
        self.save()
    
    def mark_no_show(self):
        self.status = self.NO_SHOW
        self.save()

class Donation(models.Model):
    """
    Model to track blood donations.
    """
    # Status choices for donations
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    EXPIRED = 'expired'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (APPROVED, 'Approved'),
        (REJECTED, 'Rejected'),
        (EXPIRED, 'Expired'),
    ]
    
    # Blood group choices
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    donor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='donations'
    )
    appointment = models.OneToOneField(
        Appointment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='donation'
    )
    donation_date = models.DateField()
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units = models.PositiveSmallIntegerField(default=1)
    hemoglobin_level = models.FloatField(null=True, blank=True)
    pulse_rate = models.PositiveSmallIntegerField(null=True, blank=True)
    blood_pressure = models.CharField(max_length=10, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-donation_date']
    
    def __str__(self):
        return f"{self.donor.username} - {self.blood_group} ({self.donation_date})"
    
    def approve(self):
        """Approve a donation and update inventory"""
        from inventory.models import BloodInventory
        
        self.status = self.APPROVED
        self.save()
        
        # Update inventory
        inventory, created = BloodInventory.objects.get_or_create(
            blood_group=self.blood_group,
            defaults={'units_available': 0}
        )
        inventory.units_available += self.units
        inventory.save()
        
        # Update donor's last donation date
        donor_profile = self.donor.donor_profile
        donor_profile.last_donation_date = self.donation_date
        donor_profile.save()
        
        return True
    
    def reject(self):
        self.status = self.REJECTED
        self.save()
        return True
    
    def expire(self):
        if self.status == self.APPROVED:
            # Reduce inventory when blood expires
            from inventory.models import BloodInventory
            
            self.status = self.EXPIRED
            self.save()
            
            inventory = BloodInventory.objects.get(blood_group=self.blood_group)
            inventory.units_available -= self.units
            inventory.save()
            
            return True
        return False
