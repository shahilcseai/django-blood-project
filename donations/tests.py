from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import Appointment, Donation
from accounts.models import User, DonorProfile

class AppointmentModelTest(TestCase):
    def setUp(self):
        # Create a donor user
        self.donor = User.objects.create_user(
            username='donortest',
            password='testpass123',
            email='donor@test.com',
            user_type=User.DONOR
        )
        
        # Create donor profile
        DonorProfile.objects.create(
            user=self.donor,
            phone='1234567890',
            date_of_birth='1990-01-01',
            blood_group='A+',
            address='123 Test St'
        )
        
        # Create appointments
        self.future_appointment = Appointment.objects.create(
            donor=self.donor,
            appointment_date=timezone.now() + timedelta(days=7),
            status=Appointment.PENDING
        )
        
        self.past_appointment = Appointment.objects.create(
            donor=self.donor,
            appointment_date=timezone.now() - timedelta(days=7),
            status=Appointment.PENDING
        )
    
    def test_appointment_is_upcoming(self):
        self.assertTrue(self.future_appointment.is_upcoming())
        self.assertFalse(self.past_appointment.is_upcoming())
    
    def test_appointment_is_past_due(self):
        self.assertFalse(self.future_appointment.is_past_due())
        self.assertTrue(self.past_appointment.is_past_due())
    
    def test_appointment_status_changes(self):
        # Test cancel method
        self.future_appointment.cancel()
        self.assertEqual(self.future_appointment.status, Appointment.CANCELLED)
        
        # Test confirm method
        self.past_appointment.confirm()
        self.assertEqual(self.past_appointment.status, Appointment.CONFIRMED)
        
        # Test complete method
        self.past_appointment.complete()
        self.assertEqual(self.past_appointment.status, Appointment.COMPLETED)

class DonationModelTest(TestCase):
    def setUp(self):
        # Create a donor user
        self.donor = User.objects.create_user(
            username='donortest',
            password='testpass123',
            email='donor@test.com',
            user_type=User.DONOR
        )
        
        # Create donor profile
        DonorProfile.objects.create(
            user=self.donor,
            phone='1234567890',
            date_of_birth='1990-01-01',
            blood_group='A+',
            address='123 Test St'
        )
        
        # Create a donation
        self.donation = Donation.objects.create(
            donor=self.donor,
            donation_date=timezone.now().date(),
            blood_group='A+',
            units=1,
            status=Donation.PENDING
        )
    
    def test_donation_approve(self):
        self.donation.approve()
        self.assertEqual(self.donation.status, Donation.APPROVED)
        
        # Check if inventory was updated
        from inventory.models import BloodInventory
        inventory = BloodInventory.objects.get(blood_group='A+')
        self.assertEqual(inventory.units_available, 1)
        
        # Check if donor's last donation date was updated
        self.donor.donor_profile.refresh_from_db()
        self.assertEqual(self.donor.donor_profile.last_donation_date, self.donation.donation_date)
    
    def test_donation_reject(self):
        self.donation.reject()
        self.assertEqual(self.donation.status, Donation.REJECTED)
