from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    DonorRegistrationForm, RequesterRegistrationForm,
    DonorProfileUpdateForm, RequesterProfileUpdateForm,
    UserInfoUpdateForm
)
from .models import User

def register_choice(request):
    """Display registration option (donor or requester)"""
    return render(request, 'accounts/register.html', {'choice_view': True})

def donor_register(request):
    """Handle donor registration"""
    if request.method == 'POST':
        form = DonorRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = DonorRegistrationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'user_type': 'donor',
        'choice_view': False
    })

def requester_register(request):
    """Handle requester registration"""
    if request.method == 'POST':
        form = RequesterRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful! You can now log in. Your account will be verified by an admin.')
            return redirect('login')
    else:
        form = RequesterRegistrationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'user_type': 'requester',
        'choice_view': False
    })

@login_required
def profile_view(request):
    """Display user profile based on their user type"""
    user = request.user
    
    context = {
        'user': user
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def edit_profile(request):
    """Edit user profile"""
    user = request.user
    user_form = UserInfoUpdateForm(instance=user)
    
    if user.is_donor():
        profile_form = DonorProfileUpdateForm(instance=user.donor_profile)
    else:
        profile_form = RequesterProfileUpdateForm(instance=user.requester_profile)
    
    if request.method == 'POST':
        user_form = UserInfoUpdateForm(request.POST, instance=user)
        
        if user.is_donor():
            profile_form = DonorProfileUpdateForm(request.POST, instance=user.donor_profile)
        else:
            profile_form = RequesterProfileUpdateForm(request.POST, instance=user.requester_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'user_type': user.user_type
    }
    
    return render(request, 'accounts/profile.html', {'edit_mode': True, **context})
