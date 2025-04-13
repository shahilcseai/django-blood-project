from django.test import TestCase
from django.urls import reverse
from .models import User, DonorProfile, RequesterProfile

class UserModelTest(TestCase):
    def setUp(self):
        self.donor_user = User.objects.create_user(
            username='donor1',
            password='testpass123',
            email='donor@example.com',
            user_type=User.DONOR
        )
        
        self.requester_user = User.objects.create_user(
            username='requester1',
            password='testpass123',
            email='requester@example.com',
            user_type=User.REQUESTER
        )
        
        DonorProfile.objects.create(
            user=self.donor_user,
            phone='1234567890',
            date_of_birth='1990-01-01',
            blood_group='A+',
            address='123 Test St'
        )
        
        RequesterProfile.objects.create(
            user=self.requester_user,
            organization_name='Test Hospital',
            organization_type='hospital',
            contact_phone='0987654321',
            address='456 Hospital Ave'
        )
    
    def test_user_types(self):
        self.assertTrue(self.donor_user.is_donor())
        self.assertFalse(self.donor_user.is_requester())
        
        self.assertTrue(self.requester_user.is_requester())
        self.assertFalse(self.requester_user.is_donor())
    
    def test_donor_profile(self):
        profile = self.donor_user.donor_profile
        self.assertEqual(profile.blood_group, 'A+')
        self.assertEqual(profile.phone, '1234567890')
    
    def test_requester_profile(self):
        profile = self.requester_user.requester_profile
        self.assertEqual(profile.organization_name, 'Test Hospital')
        self.assertEqual(profile.organization_type, 'hospital')

class RegisterViewTest(TestCase):
    def test_donor_registration_view(self):
        response = self.client.get(reverse('donor_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
    
    def test_requester_registration_view(self):
        response = self.client.get(reverse('requester_register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register.html')
