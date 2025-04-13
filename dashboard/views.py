from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
import json

from accounts.models import User, DonorProfile
from donations.models import Donation, Appointment
from inventory.models import BloodInventory
# Use an alias for the 'requests' app to avoid conflict with the Python 'requests' package
from requests.models import BloodRequest as BloodRequestModel

# Use BloodRequestModel instead of BloodRequest throughout the file
BloodRequest = BloodRequestModel

@login_required
def dashboard(request):
    """Main dashboard view based on user role"""
    user = request.user
    context = {}
    
    # Common dashboard data
    inventory = BloodInventory.objects.all().order_by('blood_group')
    context['inventory'] = inventory
    
    # Get blood type data for chart
    blood_data = {
        'labels': [item.blood_group for item in inventory],
        'data': [item.units_available for item in inventory],
    }
    context['blood_data_json'] = json.dumps(blood_data)
    
    # Donor dashboard
    if user.is_donor():
        # Get donor profile
        donor_profile = user.donor_profile
        context['donor_profile'] = donor_profile
        
        # Recent donations
        recent_donations = Donation.objects.filter(
            donor=user
        ).order_by('-donation_date')[:5]
        context['recent_donations'] = recent_donations
        
        # Upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            donor=user,
            appointment_date__gt=timezone.now(),
            status__in=[Appointment.PENDING, Appointment.CONFIRMED]
        ).order_by('appointment_date')[:3]
        context['upcoming_appointments'] = upcoming_appointments
        
        # Donation stats
        total_donations = Donation.objects.filter(donor=user).count()
        total_units = Donation.objects.filter(donor=user).aggregate(
            total=Sum('units')
        )['total'] or 0
        
        context['total_donations'] = total_donations
        context['total_units'] = total_units
        
        # Calculate when donor can donate again (if they have donated)
        if donor_profile.last_donation_date:
            min_days_between_donations = 90  # 3 months
            next_donation_date = donor_profile.last_donation_date + timedelta(days=min_days_between_donations)
            
            if next_donation_date > timezone.now().date():
                days_to_wait = (next_donation_date - timezone.now().date()).days
                context['days_to_wait'] = days_to_wait
                context['next_donation_date'] = next_donation_date
            else:
                context['can_donate_now'] = True
    
    # Requester dashboard
    elif user.is_requester():
        # Get requester profile
        requester_profile = user.requester_profile
        context['requester_profile'] = requester_profile
        
        # Recent requests
        recent_requests = BloodRequest.objects.filter(
            requester=user
        ).order_by('-created_at')[:5]
        context['recent_requests'] = recent_requests
        
        # Active requests
        active_requests = BloodRequest.objects.filter(
            requester=user,
            status__in=[BloodRequest.PENDING, BloodRequest.PROCESSING]
        ).count()
        context['active_requests'] = active_requests
        
        # Request stats
        fulfilled_requests = BloodRequest.objects.filter(
            requester=user, 
            status=BloodRequest.FULFILLED
        ).count()
        rejected_requests = BloodRequest.objects.filter(
            requester=user, 
            status=BloodRequest.REJECTED
        ).count()
        
        context['fulfilled_requests'] = fulfilled_requests
        context['rejected_requests'] = rejected_requests
        context['total_requests'] = recent_requests.count()
    
    # Staff/Admin dashboard
    elif user.is_staff:
        # Donation stats
        donations_today = Donation.objects.filter(
            donation_date=timezone.now().date()
        ).count()
        
        donations_this_week = Donation.objects.filter(
            donation_date__gte=timezone.now().date() - timedelta(days=7)
        ).count()
        
        context['donations_today'] = donations_today
        context['donations_this_week'] = donations_this_week
        context['total_donors'] = User.objects.filter(user_type=User.DONOR).count()
        
        # Inventory stats
        total_units = BloodInventory.objects.aggregate(total=Sum('units_available'))['total'] or 0
        context['total_units'] = total_units
        
        low_inventory = BloodInventory.objects.filter(units_available__lt=10)
        context['low_inventory'] = low_inventory
        context['low_inventory_count'] = low_inventory.count()
        
        # Request stats
        pending_requests = BloodRequest.objects.filter(
            status__in=[BloodRequest.PENDING, BloodRequest.PROCESSING]
        ).order_by('-priority', '-created_at')[:10]
        
        urgent_requests = BloodRequest.objects.filter(
            status__in=[BloodRequest.PENDING, BloodRequest.PROCESSING],
            priority__in=[BloodRequest.HIGH, BloodRequest.CRITICAL]
        ).count()
        
        context['pending_requests'] = pending_requests
        context['urgent_requests'] = urgent_requests
        context['total_requests'] = BloodRequest.objects.count()
        
        # Upcoming appointments
        upcoming_appointments = Appointment.objects.filter(
            appointment_date__gt=timezone.now(),
            appointment_date__lte=timezone.now() + timedelta(days=3),
            status__in=[Appointment.PENDING, Appointment.CONFIRMED]
        ).order_by('appointment_date')[:5]
        
        context['upcoming_appointments'] = upcoming_appointments
        
        # Blood group distribution chart
        donation_by_group = Donation.objects.filter(
            status=Donation.APPROVED
        ).values('blood_group').annotate(
            count=Count('id')
        ).order_by('blood_group')
        
        blood_group_data = {
            'labels': [item['blood_group'] for item in donation_by_group],
            'data': [item['count'] for item in donation_by_group],
        }
        context['blood_group_data_json'] = json.dumps(blood_group_data)
        
        # Time series data for donations
        last_12_months = []
        donations_by_month = []
        
        for i in range(11, -1, -1):
            month_date = timezone.now().date().replace(day=1) - timedelta(days=i*30)
            month_name = month_date.strftime('%b %Y')
            
            count = Donation.objects.filter(
                donation_date__year=month_date.year,
                donation_date__month=month_date.month
            ).count()
            
            last_12_months.append(month_name)
            donations_by_month.append(count)
        
        time_series_data = {
            'labels': last_12_months,
            'data': donations_by_month,
        }
        context['time_series_data_json'] = json.dumps(time_series_data)
    
    return render(request, 'dashboard/dashboard.html', context)

@login_required
def search(request):
    """Search functionality for donors, inventory, and requests"""
    query = request.GET.get('query', '')
    search_type = request.GET.get('type', 'all')
    
    results = {
        'donors': [],
        'inventory': [],
        'requests': [],
        'donations': []
    }
    
    if query:
        # Search for donors
        if search_type in ['all', 'donors']:
            donors = User.objects.filter(
                Q(user_type=User.DONOR) &
                (Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(donor_profile__phone__icontains=query) |
                Q(donor_profile__blood_group__icontains=query))
            )
            results['donors'] = donors
        
        # Search for inventory
        if search_type in ['all', 'inventory']:
            inventory = BloodInventory.objects.filter(
                blood_group__icontains=query
            )
            results['inventory'] = inventory
        
        # Search for requests
        if search_type in ['all', 'requests']:
            requests = BloodRequest.objects.filter(
                Q(requester__username__icontains=query) |
                Q(requester__requester_profile__organization_name__icontains=query) |
                Q(blood_group__icontains=query) |
                Q(patient_name__icontains=query) |
                Q(notes__icontains=query)
            )
            results['requests'] = requests
        
        # Search for donations
        if search_type in ['all', 'donations']:
            donations = Donation.objects.filter(
                Q(donor__username__icontains=query) |
                Q(donor__first_name__icontains=query) |
                Q(donor__last_name__icontains=query) |
                Q(blood_group__icontains=query)
            )
            results['donations'] = donations
    
    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
        'is_staff': request.user.is_staff,
    }
    
    return render(request, 'dashboard/dashboard.html', {'search_mode': True, **context})
