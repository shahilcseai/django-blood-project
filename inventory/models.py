from django.db import models
from django.conf import settings
from django.utils import timezone

class BloodInventory(models.Model):
    """
    Model to track blood inventory by blood group
    """
    BLOOD_GROUPS = [
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-'),
    ]
    
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUPS, unique=True)
    units_available = models.PositiveIntegerField(default=0)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Blood Inventory"
    
    def __str__(self):
        return f"{self.blood_group}: {self.units_available} units"
    
    def update_inventory(self, action, units, user=None, notes=None):
        """
        Update inventory based on action:
        - add: Add units to inventory
        - remove: Remove units from inventory
        - adjust: Set to exact amount
        """
        old_value = self.units_available
        
        if action == 'add':
            self.units_available += units
        elif action == 'remove':
            if self.units_available >= units:
                self.units_available -= units
            else:
                return False
        elif action == 'adjust':
            if units >= 0:
                self.units_available = units
            else:
                return False
        
        self.save()
        
        # Log the change
        InventoryLog.objects.create(
            blood_group=self.blood_group,
            action=action,
            units=units,
            old_value=old_value,
            new_value=self.units_available,
            user=user,
            notes=notes
        )
        
        return True
    
    @classmethod
    def get_total_units(cls):
        """Return total units of all blood groups"""
        return cls.objects.aggregate(models.Sum('units_available'))['units_available__sum'] or 0
    
    @classmethod
    def get_units_by_group(cls):
        """Return a dictionary of units by blood group"""
        inventory = cls.objects.all()
        return {item.blood_group: item.units_available for item in inventory}
    
    @property
    def is_low(self):
        """Check if inventory for this blood type is low (< 10 units)"""
        return self.units_available < 10

class InventoryLog(models.Model):
    """
    Model to track changes to blood inventory
    """
    ACTION_CHOICES = [
        ('add', 'Added'),
        ('remove', 'Removed'),
        ('adjust', 'Adjusted'),
        ('expired', 'Expired'),
    ]
    
    blood_group = models.CharField(max_length=3)
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    units = models.PositiveIntegerField()
    old_value = models.PositiveIntegerField()
    new_value = models.PositiveIntegerField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inventory_logs'
    )
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_action_display()} {self.units} units of {self.blood_group} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
