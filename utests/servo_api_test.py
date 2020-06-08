## @package runAllTests
import unittest
from control_interface_utest import ServoControl
from virtual_devices import VirtualServo

class TestServoControl(unittest.TestCase):
    def setUp(self):
        self.S3003 = VirtualServo([500, 3000])
        self.servo_pin_list = [0, 1, 2, 3, 4, 5]
        self.test = ServoControl()
        
    def test_initServo(self):
        for i in range(len(self.servo_pin_list)):
            pinNumber = self.servo_pin_list[i]
            init_servo_angle, init_servo_pins = self.test._initServo(self.S3003, pinNumber)
            self.assertEqual(43.2, init_servo_angle)
            self.assertEqual(pinNumber, init_servo_pins)
            
    def test_sendSignal(self):
        pwmSignal_list = [1750, 3000, 450, 800, 4000]
        groundTruth_list = [1750, 3000, 500, 800, 3000]
        for i in range(len(pwmSignal_list)):
            angle = self.test._sendSignal(self.S3003, pwmSignal_list[i])
            self.assertEqual(angle, groundTruth_list[i])
            
    def test_mapAgentActon(self):
        agent_action = [-5, -1, 0.1, 4, 5]
        groundTruth_list = []
        for i in range(len(agent_action)):
            angle = self.test._convertToPwm(self.S3003, agent_action[i])
    
if __name__ == '__main__':
    unittest.main()