## @package torch_api
#  API between pytorch package and Raspberry Pi

import os

# pytorch package used to connect with wiringPi
import torch 
import torchvision
import torchvision.transforms as transforms

import torch.nn as nn
import torch.nn.functional as F

def loadModel(path, file_name):
    model_path = os.path.join(path, file_name)    
    return torch.load(model_path)

# wiringPi package
import wiringpi

class RobotPlatform:
    def __init__(self, pinList):
        super(RobotPlatform, self).__init__()
        wiringpi.wiringPiSetup()
        self._servo_pins = pinList
        self._init_pos_signal = 9;
        self._init_servos(pinList)

    def _init_servos(self, pinList):
        for i in range(pinList):
            wiringpi.pinMode(pinList[i], OUTPUT)
            wiringpi.softPwmCreate(pinList[i], 0, 200)
            wiringpi.softPWMWrite(pinList[i], self._init_pos_signal)
        return
        
    def _actuate_Motor(self, servo_num, signal):
        wiringpi.softPwmWrite(self._servo_pins[servo_num], TEST_SIGNAL)
        wiringpi.delay(1)
        
        return
            
    def moveMotor(self, signal_pwm):
        self._actuate_Motor(signal_pwm)
            
        return
## Run a simple test for pytorch and USB

