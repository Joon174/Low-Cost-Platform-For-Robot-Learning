## @package runAllTests
import unittest
from virtual_devices import VirtualServo

class TestVirtualServo(unittest.TestCase):
    def setUp(self):
        self.S3003 = VirtualServo([500, 3000])
    
    def test_actuate(self):
        angle = self.S3003.actuate(500)
        self.assertEqual(0, angle)
        
        angle = self.S3003.actuate(1750)
        self.assertEqual(90, angle)
        
        angle = self.S3003.actuate(2375)
        self.assertEqual(135, angle)
        
        angle = self.S3003.actuate(3000)
        self.assertEqual(180, angle)