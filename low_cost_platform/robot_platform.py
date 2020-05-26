## RobotPlatform.py

# import all API packages for kernel operation:
from include.control_interface import ServoControl, MPU6050Control, PiCameraControl
from include.event_thread_handler import ThreadEvent

class RobotPlatform(ServoControl, MPU6050Control, PiCameraControl, ThreadEvent):
    def __init__(self, servo_output_pins):
        super(RobotPlatform, self).__init__(servo_output_pins)
        wiringpi.wiringPiSetup()
        self.servo = ServoControl.__init__(self, servo_output_pins)
        self.mpu6050 = MPU6050Control.__init__(self)
        self.camera = PiCameraControl.__init__(self, camera_resolution)
        self.servoEvent = ThreadEvent.__init__(self, )
        self.mpu6050Event = ThreadEvent.__init__(self, )
        self.piCameraEvent = ThreadEvent.__init__(self, )
        self.sensors = {"MPU6050", self.mpu6050Event,
                        "PiCamera", self.piCameraEvevnt}
        
    def step(self, action_space):
        self.action = action_space
        self.servoEvent.resume()
        
    def readSensor(self, sensorName):
        self.sensors[sensorName].readSensor()
        