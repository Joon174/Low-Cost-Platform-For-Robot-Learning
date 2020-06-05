from multiprocessing import Pool
form multiprocessing import cpu_count
import time
import unittest
from control_interface_mod import ServoControl
from virtual_devices import VirtualServo

def threading_cleanup():
    pass

class TestThread(Pool):
    def __init__(self, module, testcase):
        self.module = module
        self.S3003 = VirtualServo()
        self.testcase = testcase
        Pool.__init__()
        self.map(module._sendSignal, args=(, ))
        
    def run(self):
        
        self.testcase.assertEqual()
        
class BaseTestCase(unittest.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        threading_cleanup()

class ThreadTests(BaseTestCase):
    def test_servo_signal(self):
        
        