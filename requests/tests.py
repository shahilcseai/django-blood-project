from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import BloodRequest
from accounts.models import User, RequesterProfile
from inventory.models import BloodInventory

class BloodRequestModelTest(TestCase):
    def setUp(self):
        # Create a requester user
        self.requester = User.objects.create_user(
            username='requestertest',
            password='testpass123',
            email='requester@test.com',
            user_type=User.REQUESTER
        )
        
        # Create requester profile
        RequesterProfile.objects.create(
            user=self.requester,
            organization_name='Test Hospital',
            organization_type='hospital',
            contact_phone='1234567890',
            address='123 Hospital St',
            verified=True
        )
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admintest',
            password='testpass123',
            email='admin@test.com',
            is_staff=True
        )
        
        # Create blood inventory
        self.inventory = BloodInventory.objects.create(
            blood_group='A+',
            units_available=50
        )
        
        # Create blood request
        self.request = BloodRequest.objects.create(
            requester=self.requester,
            blood_group='A+',
            units_needed=5,
            priority=BloodRequest.MEDIUM,
            needed_by=timezone.now().date() + timedelta(days=7)
        )
    
    def test_is_urgent(self):
        # Test non-urgent request
        self.assertFalse(self.request.is_urgent())
        
        # Update to urgent priority
        self.request.priority = BloodRequest.CRITICAL
        self.request.save()
        self.assertTrue(self.request.is_urgent())
    
    def test_fulfill_request(self):
        # Fulfill the request
        result = self.request.fulfill(self.admin)
        self.assertTrue(result)
        
        # Check request status
        self.assertEqual(self.request.status, BloodRequest.FULFILLED)
        self.assertIsNotNone(self.request.fulfilled_date)
        
        # Check inventory was updated
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.units_available, 45)
    
    def test_reject_request(self):
        # Reject the request
        result = self.request.reject("Not enough matching blood available", self.admin)
        self.assertTrue(result)
        
        # Check request status
        self.assertEqual(self.request.status, BloodRequest.REJECTED)
        self.assertEqual(self.request.rejected_reason, "Not enough matching blood available")
    
    def test_cancel_request(self):
        # Cancel the request
        result = self.request.cancel()
        self.assertTrue(result)
        
        # Check request status
        self.assertEqual(self.request.status, BloodRequest.CANCELLED)
