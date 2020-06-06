# !/usr/bin/env/python3
## RobotPlatform.py
# import all API packages for kernel operation:
from include.control_interface import ServoControl, MPU6050Control
from include.event_thread_handler import ThreadEvent
import wiringpi
from picamera import PiCamera

class RobotPlatform(ServoControl, MPU6050Control, ThreadEvent):
    def __init__(self, servo_output_pins, camera_resolution):
        wiringpi.wiringPiSetup()
        self.servo = ServoControl(servo_output_pins)
        self.mpu6050 = MPU6050Control()
        self.sensors = {"S3003", self.servo,
                        "MPU6050", self.mpu6050}
        
    def readSensor(self, sensorName):
        return self.sensors[sensorName].readSensor()
        
    def step(self, servo_idx, pwm_signal):
        self.servo.moveMotor(servo_idx, pwm_signal)
        servo_pos = self.servo.readSensor("S3003")
        body_pos = self.servo.readSensor("MPU6050")
        
        return servo_pos, body_pos
    
    def reset(self):
        self.servo._init_servo_pos()
        self.mpu6050._init_pos()
        