import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Q
from .models import BloodRequest
from .forms import BloodRequestForm, RequestResponseForm
from inventory.models import BloodInventory

@login_required
def request_list(request):
    """View blood requests based on user role"""
    user = request.user
    
    if user.is_staff:
        # Staff can see all requests with filtering options
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        blood_group_filter = request.GET.get('blood_group', '')
        
        requests = BloodRequest.objects.all()
        
        if status_filter:
            requests = requests.filter(status=status_filter)
        
        if priority_filter:
            requests = requests.filter(priority=priority_filter)
        
        if blood_group_filter:
            requests = requests.filter(blood_group=blood_group_filter)
        
        # Add count of urgent requests
        urgent_count = BloodRequest.objects.filter(
            priority__in=[BloodRequest.HIGH, BloodRequest.CRITICAL],
            status__in=[BloodRequest.PENDING, BloodRequest.PROCESSING]
        ).count()
        
        context = {
            'requests': requests,
            'is_staff': True,
            'status_filter': status_filter,
            'priority_filter': priority_filter,
            'blood_group_filter': blood_group_filter,
            'urgent_count': urgent_count,
            'status_choices': BloodRequest.STATUS_CHOICES,
            'priority_choices': BloodRequest.PRIORITY_CHOICES,
            'blood_group_choices': BloodRequest.BLOOD_GROUPS
        }
        
    elif user.is_requester():
        # Requesters can see only their requests
        requests = BloodRequest.objects.filter(requester=user)
        
        context = {
            'requests': requests,
            'is_staff': False
        }
        
    else:
        messages.error(request, "You don't have permission to view blood requests.")
        return redirect('dashboard')
    
    return render(request, 'requests/request_list.html', context)

@login_required
def create_request(request):
    """Create a new blood request"""
    if not request.user.is_requester():
        messages.error(request, "Only registered requesters can create blood requests.")
        return redirect('dashboard')
    
    # Check if requester is verified
    if not request.user.requester_profile.verified:
        messages.warning(
            request, 
            "Your account is not verified yet. You can submit requests, but they will not be processed until verification."
        )
    
    # Check current inventory to show available units
    inventory = BloodInventory.objects.all()
    inventory_levels = {item.blood_group: item.units_available for item in inventory}
    
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_request = form.save(commit=False)
            blood_request.requester = request.user
            
            # For critical requests, set needed_by to today
            if blood_request.priority == BloodRequest.CRITICAL:
                blood_request.needed_by = timezone.now().date()
            
            blood_request.save()
            
            messages.success(
                request, 
                "Blood request submitted successfully. You will be notified when it's processed."
            )
            return redirect('request_list')
    else:
        form = BloodRequestForm()
    
    context = {
        'form': form,
        'inventory_levels': inventory_levels
    }
    
    return render(request, 'requests/request_form.html', context)

@login_required
def request_detail(request, request_id):
    """View details of a specific blood request"""
    # Determine if user can view this request
    if request.user.is_staff:
        blood_request = get_object_or_404(BloodRequest, id=request_id)
    elif request.user.is_requester():
        blood_request = get_object_or_404(BloodRequest, id=request_id, requester=request.user)
    else:
        messages.error(request, "You don't have permission to view this request.")
        return redirect('dashboard')
    
    # Check inventory for this blood group
    try:
        inventory = BloodInventory.objects.get(blood_group=blood_request.blood_group)
        available_units = inventory.units_available
    except BloodInventory.DoesNotExist:
        available_units = 0
    
    context = {
        'blood_request': blood_request,
        'available_units': available_units,
        'is_staff': request.user.is_staff,
        'can_respond': request.user.is_staff and blood_request.status in [
            BloodRequest.PENDING, BloodRequest.PROCESSING
        ],
        'can_cancel': blood_request.requester == request.user and blood_request.status in [
            BloodRequest.PENDING, BloodRequest.PROCESSING
        ]
    }
    
    return render(request, 'requests/request_detail.html', context)

@login_required
def cancel_request(request, request_id):
    """Cancel a blood request"""
    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        requester=request.user,
        status__in=[BloodRequest.PENDING, BloodRequest.PROCESSING]
    )
    
    if request.method == 'POST':
        blood_request.cancel()
        messages.success(request, "Blood request cancelled successfully.")
        return redirect('request_list')
    
    return render(request, 'requests/request_form.html', {
        'blood_request': blood_request,
        'cancel_mode': True
    })

@login_required
def respond_to_request(request, request_id):
    """Respond to a blood request - staff only"""
    if not request.user.is_staff:
        messages.error(request, "Only staff members can respond to blood requests.")
        return redirect('dashboard')
    
    blood_request = get_object_or_404(
        BloodRequest,
        id=request_id,
        status__in=[BloodRequest.PENDING, BloodRequest.PROCESSING]
    )
    
    # Check inventory for this blood group
    try:
        inventory = BloodInventory.objects.get(blood_group=blood_request.blood_group)
        available_units = inventory.units_available
    except BloodInventory.DoesNotExist:
        available_units = 0
    
    if request.method == 'POST':
        form = RequestResponseForm(request.POST)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            rejected_reason = form.cleaned_data['rejected_reason']
            admin_notes = form.cleaned_data['admin_notes']
            
            if new_status == BloodRequest.FULFILLED:
                # Check if enough inventory is available
                if available_units < blood_request.units_needed:
                    messages.error(
                        request,
                        f"Not enough {blood_request.blood_group} units available. Need {blood_request.units_needed}, have {available_units}."
                    )
                    return redirect('respond_to_request', request_id=request_id)
                
                # Update blood request and inventory
                result = blood_request.fulfill(request.user)
                
                if result:
                    messages.success(request, "Blood request fulfilled successfully.")
                else:
                    messages.error(request, "Failed to fulfill blood request.")
            
            elif new_status == BloodRequest.REJECTED:
                blood_request.reject(rejected_reason, request.user)
                messages.success(request, "Blood request rejected.")
            
            else:
                # Just update the status
                blood_request.status = new_status
                blood_request.admin_notes = admin_notes
                blood_request.save()
                messages.success(request, f"Blood request status updated to {blood_request.get_status_display()}.")
            
            return redirect('request_list')
    else:
        form = RequestResponseForm(initial={'status': blood_request.status})
    
    context = {
        'form': form,
        'blood_request': blood_request,
        'available_units': available_units,
        'enough_inventory': available_units >= blood_request.units_needed
    }
    
    return render(request, 'requests/request_form.html', {'response_mode': True, **context})

@login_required
def export_requests(request):
    """Export blood requests to CSV - staff only"""
    if not request.user.is_staff:
        messages.error(request, "Only staff members can export blood requests.")
        return redirect('request_list')
    
    # Apply filters if provided
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    blood_group_filter = request.GET.get('blood_group', '')
    
    requests = BloodRequest.objects.all()
    
    if status_filter:
        requests = requests.filter(status=status_filter)
    
    if priority_filter:
        requests = requests.filter(priority=priority_filter)
    
    if blood_group_filter:
        requests = requests.filter(blood_group=blood_group_filter)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="blood_requests.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'ID', 'Requester', 'Organization', 'Blood Group', 'Units Needed',
        'Priority', 'Needed By', 'Status', 'Created', 'Fulfilled/Rejected Date',
        'Patient Name', 'Notes', 'Rejection Reason'
    ])
    
    for req in requests:
        writer.writerow([
            req.id,
            req.requester.get_full_name() or req.requester.username,
            req.requester.requester_profile.organization_name,
            req.blood_group,
            req.units_needed,
            req.get_priority_display(),
            req.needed_by.strftime('%Y-%m-%d') if req.needed_by else 'N/A',
            req.get_status_display(),
            req.created_at.strftime('%Y-%m-%d %H:%M'),
            req.fulfilled_date.strftime('%Y-%m-%d %H:%M') if req.fulfilled_date else 'N/A',
            req.patient_name or 'N/A',
            req.notes or 'N/A',
            req.rejected_reason or 'N/A'
        ])
    
    return response
