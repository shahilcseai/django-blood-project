from django.contrib import admin
from .models import BloodRequest

@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
    list_display = ('requester', 'blood_group', 'units_needed', 'priority', 'status', 'created_at')
    list_filter = ('status', 'priority', 'blood_group', 'created_at')
    search_fields = ('requester__username', 'requester__requester_profile__organization_name', 'notes')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Request Information', {
            'fields': ('requester', 'blood_group', 'units_needed', 'priority', 'needed_by', 'notes')
        }),
        ('Status Information', {
            'fields': ('status', 'fulfilled_date', 'rejected_reason')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """When a request is fulfilled, automatically deduct from inventory"""
        if change and 'status' in form.changed_data:
            if obj.status == BloodRequest.FULFILLED and form.initial['status'] != BloodRequest.FULFILLED:
                # Request is being fulfilled now
                from inventory.models import BloodInventory
                inventory = BloodInventory.objects.get(blood_group=obj.blood_group)
                inventory.update_inventory('remove', obj.units_needed, request.user, f"Fulfilled request #{obj.id}")
            
            # Set fulfilled date
            if obj.status == BloodRequest.FULFILLED and not obj.fulfilled_date:
                from django.utils import timezone
                obj.fulfilled_date = timezone.now()
                
        super().save_model(request, obj, form, change)
