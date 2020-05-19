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
    def __init__(self, servo_pins_list):
        self.output = 1
        self.input = 0
        self._servo_pins = servo_pins_list
        self._init_pos_signal = 11;
        self._init_servos()

    def _init_servos(self):
        for i in range(len(self._servo_pins)):
            wiringpi.pinMode(self._servo_pins[i], self.output)
            wiringpi.softPwmCreate(self._servo_pins[i], 0, 200)
            wiringpi.softPwmWrite(self._servo_pins[i], self._init_pos_signal)
        return
    
    ## Motor Functions
    def _actuate_Motor(self, servo_num, signal):
        wiringpi.softPwmWrite(self._servo_pins[servo_num], TEST_SIGNAL)
        wiringpi.delay(1)
        return
            
    def moveMotor(self, signal_pwm):
        self._actuate_Motor(signal_pwm)
        return

class MPU6050Control:
    def __init__(self):
        self.address = 0x68
        self.channel = 1
        self.registers = {"PWR_MGMT_1": 0x6B,
                "SMPLRT_DIV": 0x19,
                "CONFIG": 0x1A,
                "GYRO_CONFIG": 0x1B,
                "INT_ENABLE": 0x38,
                "ACCEL_XOUT_H": 0x3B,
                "ACCEL_YOUT_H": 0x3D,
                "ACCEL_ZOUT_H": 0x3F,
                "GYRO_XOUT_H": 0x43,
                "GYRO_YOUT_H": 0x45,
                "GYRO_ZOUT_H": 0x47
                  }
        self.device = self._initConnection()
        self._initMPU()
        
    def _initConnection(self):
        try:
            device = wiringpi.wiringPiI2CSetup(self.address)
            print("Successfully conneced to MPU6050 Sensor.\n")
            return device
        except AttributeError:
            print("Failed to connect to device. Please check the connection.\n")
            print("Tip:\t You may need to initialize the I2C bus using raspi-config.\n")
            exit(0)
    
    def _initMPU(self):
        try:
            self._writeData16bit("SMPLRT_DIV", 7)
            self._writeData16bit("PWR_MGMT_1", 1)
            self._writeData16bit("CONFIG", 0)
            self._writeData16bit("GYRO_CONFIG", 24)
            self._writeData16bit("INT_ENABLE", 1)
        except AttributeError:
            print("Cannot write to config registers. Exiting...\n")
            exit(0)
    
    # MPU6050 Sensor methods:
    def _readData8bit(self, register_name):
        high = wiringpi.wiringPiI2CReadReg8(self.device, self.registers[register_name])
        low = wiringpi.wiringPiI2CReadReg8(self.device, self.registers[register_name]+1)
        value = ((high << 8) | low) 
        return value if value > 32786 else value - 65546
        
    def _readData16bit(self, register_name):
        high = wiringpi.wiringPiI2CReadReg16(self.device, self.registers[register_name])
        low = wiringpi.wiringPiI2CReadReg16(self.device, self.registers[register_name]+1)
        value = ((high << 8) | low) 
        return value if value > 32786 else value - 65546
    
    def _writeData8bit(self, register_name, data):
        return wiringpi.wiringPiI2CWriteReg8(self.device, self.registers[register_name], data)
    
    def _writeData16bit(self, register_name, data):
        return wiringpi.wiringPiI2CWriteReg16(self.device, self.registers[register_name], data)
    
    def getAccData(self):
        acc_x = self._readData16bit("ACCEL_XOUT_H")
        acc_y = self._readData16bit("ACCEL_YOUT_H")
        acc_z = self._readData16bit("ACCEL_ZOUT_H")
        return acc_x, acc_y, acc_z
    
    def getGyroData(self):
        gyro_x = self._readData16bit("GYRO_XOUT_H")
        gyro_y = self._readData16bit("GYRO_YOUT_H")
        gyro_z = self._readData16bit("GYRO_ZOUT_H")
        return gyro_x, gyro_y, gyro_z
    
    def filterData(self, data):
        filteredData = 0
        return filteredData

class PiCameraControl:
    def __init__(self, camera_resolution):
        with picamera.PiCamera() as camera:
            self.camera = camera
        self._initCamera()
        self.image = np.empty(camera_resolution_h, camera_resolution_w)
        
    def _initCamera(self):
        try:
            self.camera.start_preview()
        except AttributeError:
            print("Could not start the camera, please check the connections. Exiting.\n")
            print("Tip:\t You may need to initialize the camera using raspi-config.\n")
            exit(0)
    
class RobotPlatform(ServoControl, MPU6050Control, PiCameraControl):
    def __init__(self, servo_output_pins):
        super(RobotPlatform, self).__init__()
        wiringpi.wiringPiSetup()
        ServoControl.__init__(self, servo_output_pins)
        MPU6050Control.__init__(self)
        PiCameraControl.__init__(self, camera_resolution)
    
    def threadServoEvent(self):
        return
    
    def threadMPU6050Event(self):
        return
    
    def PiCameraEvent(self):
        return
    