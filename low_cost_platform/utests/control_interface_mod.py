## @package torch_api
#  API between pytorch package and Raspberry Pi

# packages for processing
import numpy as np
import cv2

# packages for kernel operations
import wiringpi
import picamera
from PIL import Image

class ServoControl:
    def __init__(self):
        super(ServoControl, self).__init__()
        self._init_pos_signal = 1100
        self._emulateAgentAction = 1750

    def _initServo(self, servo, pinNumber):
        self.servo = servo
        pinNumber = self.servo.setPin(pinNumber)
        servo_angle = self.servo.actuate(self._init_pos_signal)
        return servo_angle, pinNumber
    
    def _sendSignal(self, servo, pwmSignal):
        if pwmSignal < servo.min_width:
            pwmSignal = servo.min_width
        elif pwmSignal > servo.max_width:
            pwmSignal = servo.max_width
        return pwmSignal
    