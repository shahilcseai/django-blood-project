from django.test import TestCase
from django.urls import reverse
from .models import BloodInventory, InventoryLog
from accounts.models import User

class BloodInventoryModelTest(TestCase):
    def setUp(self):
        # Create test user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            password='testpass123',
            email='staff@test.com',
            is_staff=True
        )
        
        # Create inventory
        self.inventory = BloodInventory.objects.create(
            blood_group='A+',
            units_available=20
        )
    
    def test_add_inventory(self):
        # Test adding units
        self.inventory.update_inventory('add', 10, self.staff_user, 'Testing add')
        self.assertEqual(self.inventory.units_available, 30)
        
        # Check log was created
        log = InventoryLog.objects.first()
        self.assertEqual(log.action, 'add')
        self.assertEqual(log.units, 10)
        self.assertEqual(log.old_value, 20)
        self.assertEqual(log.new_value, 30)
        self.assertEqual(log.user, self.staff_user)
    
    def test_remove_inventory(self):
        # Test removing units
        self.inventory.update_inventory('remove', 5, self.staff_user, 'Testing remove')
        self.assertEqual(self.inventory.units_available, 15)
        
        # Check log was created
        log = InventoryLog.objects.first()
        self.assertEqual(log.action, 'remove')
        self.assertEqual(log.units, 5)
        self.assertEqual(log.old_value, 20)
        self.assertEqual(log.new_value, 15)
    
    def test_remove_too_many_units(self):
        # Try to remove more units than available
        result = self.inventory.update_inventory('remove', 25, self.staff_user, 'Testing remove too many')
        self.assertFalse(result)
        self.assertEqual(self.inventory.units_available, 20)
        
        # No log should be created
        self.assertEqual(InventoryLog.objects.count(), 0)
    
    def test_adjust_inventory(self):
        # Test adjusting to exact amount
        self.inventory.update_inventory('adjust', 50, self.staff_user, 'Testing adjust')
        self.assertEqual(self.inventory.units_available, 50)
        
        # Check log was created
        log = InventoryLog.objects.first()
        self.assertEqual(log.action, 'adjust')
        self.assertEqual(log.units, 50)
        self.assertEqual(log.old_value, 20)
        self.assertEqual(log.new_value, 50)
