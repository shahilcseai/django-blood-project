import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Appointment, Donation
from .forms import AppointmentForm, DonationForm
from .utils import generate_donation_pdf

@login_required
def appointment_list(request):
    """View all appointments for a donor"""
    if not request.user.is_donor():
        messages.error(request, "Only donors can view appointments.")
        return redirect('dashboard')
    
    # Get upcoming and past appointments
    upcoming_appointments = Appointment.objects.filter(
        donor=request.user,
        appointment_date__gt=timezone.now(),
        status__in=[Appointment.PENDING, Appointment.CONFIRMED]
    ).order_by('appointment_date')
    
    past_appointments = Appointment.objects.filter(
        donor=request.user
    ).exclude(
        id__in=upcoming_appointments.values_list('id', flat=True)
    ).order_by('-appointment_date')
    
    context = {
        'upcoming_appointments': upcoming_appointments,
        'past_appointments': past_appointments
    }
    
    return render(request, 'donations/appointments.html', context)

@login_required
def create_appointment(request):
    """Create a new appointment for a donor"""
    if not request.user.is_donor():
        messages.error(request, "Only donors can create appointments.")
        return redirect('dashboard')
    
    # Check if donor has a recent donation (within 3 months)
    donor_profile = request.user.donor_profile
    if donor_profile.last_donation_date:
        last_donation = donor_profile.last_donation_date
        min_days_between_donations = 90  # 3 months
        
        if (timezone.now().date() - last_donation).days < min_days_between_donations:
            days_to_wait = min_days_between_donations - (timezone.now().date() - last_donation).days
            messages.warning(
                request, 
                f"For health reasons, you can't donate again for {days_to_wait} more days. "
                f"Your last donation was on {last_donation}."
            )
            return redirect('appointment_list')
    
    # Check if user already has an upcoming appointment
    has_upcoming = Appointment.objects.filter(
        donor=request.user,
        appointment_date__gt=timezone.now(),
        status__in=[Appointment.PENDING, Appointment.CONFIRMED]
    ).exists()
    
    if has_upcoming:
        messages.info(request, "You already have an upcoming appointment. Please cancel it before creating a new one.")
        return redirect('appointment_list')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.donor = request.user
            appointment.save()
            
            messages.success(request, "Appointment scheduled successfully! We'll contact you to confirm.")
            return redirect('appointment_list')
    else:
        form = AppointmentForm()
    
    return render(request, 'donations/appointment_form.html', {'form': form})

@login_required
def cancel_appointment(request, pk):
    """Cancel an existing appointment"""
    appointment = get_object_or_404(Appointment, pk=pk, donor=request.user)
    
    if not appointment.is_upcoming():
        messages.error(request, "Cannot cancel a past appointment or one that's already cancelled.")
        return redirect('appointment_list')
    
    if request.method == 'POST':
        appointment.cancel()
        messages.success(request, "Appointment cancelled successfully.")
        return redirect('appointment_list')
    
    return render(request, 'donations/appointment_form.html', {
        'appointment': appointment,
        'cancel_mode': True
    })

@login_required
def complete_appointment(request, pk):
    """Mark an appointment as completed - staff only"""
    if not request.user.is_staff:
        messages.error(request, "Only staff members can complete appointments.")
        return redirect('dashboard')
    
    appointment = get_object_or_404(Appointment, pk=pk)
    
    if appointment.status == Appointment.COMPLETED:
        messages.info(request, "This appointment is already marked as completed.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donation = form.save(commit=False)
            donation.donor = appointment.donor
            donation.appointment = appointment
            donation.save()
            
            # Mark the appointment as completed
            appointment.complete()
            
            messages.success(request, "Appointment completed and donation recorded successfully.")
            return redirect('dashboard')
    else:
        # Pre-fill the form with donor's blood type
        initial_data = {
            'blood_group': appointment.donor.donor_profile.blood_group,
            'donation_date': timezone.now().date()
        }
        form = DonationForm(initial=initial_data)
    
    return render(request, 'donations/appointment_form.html', {
        'appointment': appointment,
        'form': form,
        'complete_mode': True
    })

@login_required
def donation_history(request):
    """View donation history for a donor"""
    if request.user.is_donor():
        donations = Donation.objects.filter(donor=request.user).order_by('-donation_date')
    elif request.user.is_staff:
        donor_id = request.GET.get('donor_id')
        if donor_id:
            donations = Donation.objects.filter(donor_id=donor_id).order_by('-donation_date')
        else:
            donations = Donation.objects.all().order_by('-donation_date')
    else:
        messages.error(request, "You don't have permission to view donation history.")
        return redirect('dashboard')
    
    context = {
        'donations': donations
    }
    
    return render(request, 'donations/donation_history.html', context)

@login_required
def record_donation(request):
    """Record a new donation - staff only"""
    if not request.user.is_staff:
        messages.error(request, "Only staff members can record donations.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = DonationForm(request.POST)
        if form.is_valid():
            donor_id = request.POST.get('donor_id')
            donor = get_object_or_404(User, id=donor_id, user_type=User.DONOR)
            
            donation = form.save(commit=False)
            donation.donor = donor
            donation.save()
            
            # Auto-approve the donation
            donation.approve()
            
            messages.success(request, "Donation recorded and approved successfully.")
            return redirect('donation_history')
    else:
        form = DonationForm()
    
    return render(request, 'donations/appointment_form.html', {
        'form': form,
        'donation_mode': True
    })

@login_required
def export_donation_history(request):
    """Export donation history as CSV or PDF"""
    if not request.user.is_donor() and not request.user.is_staff:
        messages.error(request, "You don't have permission to export donation history.")
        return redirect('dashboard')
    
    # Determine which donations to export
    if request.user.is_donor():
        donations = Donation.objects.filter(donor=request.user).order_by('-donation_date')
        filename = f"donations_{request.user.username}"
    elif request.user.is_staff:
        donor_id = request.GET.get('donor_id')
        if donor_id:
            donations = Donation.objects.filter(donor_id=donor_id).order_by('-donation_date')
            donor = get_object_or_404(User, id=donor_id)
            filename = f"donations_{donor.username}"
        else:
            donations = Donation.objects.all().order_by('-donation_date')
            filename = "all_donations"
    
    # Determine export format
    export_format = request.GET.get('format', 'csv')
    
    if export_format == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Donor', 'Date', 'Blood Group', 'Units', 'Status'])
        
        for donation in donations:
            writer.writerow([
                donation.donor.get_full_name(),
                donation.donation_date,
                donation.blood_group,
                donation.units,
                donation.get_status_display()
            ])
        
        return response
    
    elif export_format == 'pdf':
        return generate_donation_pdf(donations, filename)
    
    else:
        messages.error(request, "Invalid export format.")
        return redirect('donation_history')
