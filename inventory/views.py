import csv
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from .models import BloodInventory, InventoryLog
from .forms import InventoryUpdateForm

@login_required
def inventory_list(request):
    """View blood inventory status"""
    inventory = BloodInventory.objects.all().order_by('blood_group')
    
    # Check if any inventory needs to be created
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    existing_groups = inventory.values_list('blood_group', flat=True)
    
    # Initialize missing blood groups
    for group in blood_groups:
        if group not in existing_groups:
            BloodInventory.objects.create(blood_group=group, units_available=0)
    
    # Re-fetch data if we added new groups
    if len(existing_groups) < len(blood_groups):
        inventory = BloodInventory.objects.all().order_by('blood_group')
    
    # Calculate totals
    total_units = BloodInventory.get_total_units()
    
    # Identify low inventory
    low_inventory = [item for item in inventory if item.is_low]
    
    context = {
        'inventory': inventory,
        'total_units': total_units,
        'low_inventory': low_inventory,
        'can_update': request.user.is_staff
    }
    
    return render(request, 'inventory/inventory_list.html', context)

@login_required
def update_inventory(request):
    """Update blood inventory - staff only"""
    if not request.user.is_staff:
        messages.error(request, "Only staff members can update inventory.")
        return redirect('inventory_list')
    
    if request.method == 'POST':
        form = InventoryUpdateForm(request.POST)
        if form.is_valid():
            blood_group = form.cleaned_data['blood_group']
            action = form.cleaned_data['action']
            units = form.cleaned_data['units']
            notes = form.cleaned_data['notes']
            
            inventory, created = BloodInventory.objects.get_or_create(
                blood_group=blood_group,
                defaults={'units_available': 0}
            )
            
            result = inventory.update_inventory(action, units, request.user, notes)
            
            if result:
                action_display = 'added to' if action == 'add' else 'removed from' if action == 'remove' else 'adjusted in'
                messages.success(request, f"Successfully {action_display} {blood_group} inventory.")
            else:
                messages.error(request, "Failed to update inventory. Please check the values.")
            
            return redirect('inventory_list')
    else:
        form = InventoryUpdateForm()
    
    return render(request, 'inventory/add_inventory.html', {'form': form})

@login_required
def inventory_logs(request):
    """View inventory change logs - staff only"""
    if not request.user.is_staff:
        messages.error(request, "Only staff members can view inventory logs.")
        return redirect('inventory_list')
    
    logs = InventoryLog.objects.all().order_by('-created_at')
    
    # Apply filters if provided
    blood_group = request.GET.get('blood_group')
    action = request.GET.get('action')
    
    if blood_group:
        logs = logs.filter(blood_group=blood_group)
    
    if action:
        logs = logs.filter(action=action)
    
    context = {
        'logs': logs,
        'blood_groups': ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'],
        'actions': [choice[0] for choice in InventoryLog.ACTION_CHOICES],
        'selected_blood_group': blood_group,
        'selected_action': action
    }
    
    return render(request, 'inventory/inventory_list.html', {'log_view': True, **context})

@login_required
def export_inventory(request):
    """Export inventory data to CSV - staff only"""
    if not request.user.is_staff:
        messages.error(request, "Only staff members can export inventory data.")
        return redirect('inventory_list')
    
    # Determine what to export
    export_type = request.GET.get('type', 'current')
    
    if export_type == 'current':
        # Export current inventory
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="blood_inventory.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Blood Group', 'Units Available', 'Last Updated'])
        
        inventory = BloodInventory.objects.all().order_by('blood_group')
        for item in inventory:
            writer.writerow([
                item.blood_group,
                item.units_available,
                item.last_updated.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
    elif export_type == 'logs':
        # Export inventory logs
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="inventory_logs.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Blood Group', 'Action', 'Units', 'Old Value', 'New Value', 'User', 'Notes'])
        
        logs = InventoryLog.objects.all().order_by('-created_at')
        
        # Apply filters if provided
        blood_group = request.GET.get('blood_group')
        action = request.GET.get('action')
        
        if blood_group:
            logs = logs.filter(blood_group=blood_group)
        
        if action:
            logs = logs.filter(action=action)
        
        for log in logs:
            writer.writerow([
                log.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                log.blood_group,
                log.get_action_display(),
                log.units,
                log.old_value,
                log.new_value,
                log.user.username if log.user else 'System',
                log.notes or ''
            ])
    
    else:
        messages.error(request, "Invalid export type.")
        return redirect('inventory_list')
    
    return response
