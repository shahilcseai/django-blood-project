from django.contrib import admin
from .models import BloodInventory, InventoryLog

@admin.register(BloodInventory)
class BloodInventoryAdmin(admin.ModelAdmin):
    list_display = ('blood_group', 'units_available', 'last_updated')
    list_filter = ('blood_group',)
    search_fields = ('blood_group',)
    readonly_fields = ('last_updated',)

@admin.register(InventoryLog)
class InventoryLogAdmin(admin.ModelAdmin):
    list_display = ('blood_group', 'action', 'units', 'created_at', 'user')
    list_filter = ('action', 'blood_group', 'created_at')
    search_fields = ('blood_group', 'user__username')
    date_hierarchy = 'created_at'
