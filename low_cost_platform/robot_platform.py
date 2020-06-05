# !/usr/bin/env/python3
## RobotPlatform.py
# import all API packages for kernel operation:
from include.control_interface import ServoControl, MPU6050Control, PiCameraControl
from include.event_thread_handler import ThreadEvent

class RobotPlatform(ServoControl, MPU6050Control, PiCameraControl, ThreadEvent):
    def __init__(self, servo_output_pins, camera_resolution = [328, 168]):
        super(RobotPlatform, self).__init__()
        wiringpi.wiringPiSetup()
        self.servo = ServoControl.__init__(self, servo_output_pins)
        self.mpu6050 = MPU6050Control.__init__(self)
        self.camera = PiCameraControl.__init__(self, camera_resolution)
        self.sensors = {"S3003", self.servo,
                        "MPU6050", self.mpu6050,
                        "PiCamera", self.camera}
        
    def readSensor(self, sensorName):
        return self.sensors[sensorName].readSensor()
        
    def step(self, servo_idx, pwm_signal):
        servo_pos = self.servo.moveMotor(servo_idx, pwm_signal)
        body_pos = self.servo.readSensor("MPU6050")
        image_cap = self.servo.readSensor("PiCamera")
        
        return servo_pos, body_pos, image_cap
    
    def reset(self):
        self.servo._init_servo_pos()
        self.mpu6050._init_pos()
        