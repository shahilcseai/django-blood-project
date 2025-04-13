from django.db import models
from django.conf import settings
from django.utils import timezone

class BloodRequest(models.Model):
    """Model to track blood requests from requesters"""
    # Status choices
    PENDING = 'pending'
    PROCESSING = 'processing'
    FULFILLED = 'fulfilled'
    REJECTED = 'rejected'
    CANCELLED = 'cancelled'
    
    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (PROCESSING, 'Processing'),
        (FULFILLED, 'Fulfilled'),
        (REJECTED, 'Rejected'),
        (CANCELLED, 'Cancelled'),
    ]
    
    # Priority choices
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    CRITICAL = 'critical'
    
    PRIORITY_CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
        (CRITICAL, 'Critical'),
    ]
    
    # Blood group choices
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blood_requests'
    )
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS)
    units_needed = models.PositiveIntegerField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default=MEDIUM)
    needed_by = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    patient_name = models.CharField(max_length=100, blank=True, null=True)
    
    # Status tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    fulfilled_date = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(blank=True, null=True)
    admin_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.requester.username} - {self.blood_group} ({self.get_status_display()})"
    
    def is_urgent(self):
        return self.priority in [self.HIGH, self.CRITICAL]
    
    def is_past_due(self):
        if self.needed_by and self.status in [self.PENDING, self.PROCESSING]:
            return self.needed_by < timezone.now().date()
        return False
    
    def fulfill(self, admin_user=None):
        """Mark request as fulfilled and update inventory"""
        if self.status == self.FULFILLED:
            return False
        
        # Check if enough inventory is available
        from inventory.models import BloodInventory
        inventory = BloodInventory.objects.get(blood_group=self.blood_group)
        
        if inventory.units_available < self.units_needed:
            return False
        
        # Update inventory
        inventory.update_inventory(
            'remove', 
            self.units_needed, 
            admin_user,
            f"Fulfilled request #{self.id} for {self.requester.username}"
        )
        
        # Update request status
        self.status = self.FULFILLED
        self.fulfilled_date = timezone.now()
        self.save()
        
        return True
    
    def reject(self, reason, admin_user=None):
        """Reject a blood request with reason"""
        if not reason:
            return False
        
        self.status = self.REJECTED
        self.rejected_reason = reason
        self.save()
        
        return True
    
    def cancel(self):
        """Cancel a blood request (by requester)"""
        if self.status in [self.FULFILLED, self.REJECTED]:
            return False
        
        self.status = self.CANCELLED
        self.save()
        
        return True
