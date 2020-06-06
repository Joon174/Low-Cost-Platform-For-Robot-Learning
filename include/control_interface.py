## @package torch_api
#  API between pytorch package and Raspberry Pi

# packages for processing
import numpy as np
import math
import cv2
import time

# packages for kernel operations
import threading
import wiringpi
from picamera import PiCamera
from PIL import Image
from include.filters import Kalman

class ServoControl:
    def __init__(self, servo_pins_list):
        super(ServoControl, self).__init__()
        self.output = 1
        self.input = 0
        self._servo_pins = servo_pins_list
        self.servo_pos = 0
        self.servo_pwm_min = 550
        self.servo_pwm_max = 3000
        self._init_pos_signal = 11;
        self._init_servos()
        self.dt = 0.1

    def _init_servos(self):
        for i in range(len(self._servo_pins)):
            wiringpi.pinMode(self._servo_pins[i], self.output)
            wiringpi.softPwmCreate(self._servo_pins[i], 0, 200)
            wiringpi.softPwmWrite(self._servo_pins[i], self._init_pos_signal)
    
    def _init_servo_pos(self):
        for i in range(len(self._servo_pins)):
            wiringpi.softPwmCreate(self._servo_pins[i], 0, 200)
            wiringpi.softPwmWrite(self._servo_pins[i], self._init_pos_signal)        
    
    ## Motor Functions
    def _actuate_Motor(self, servo_num, signal):
        self.servo_pos = signal
        wiringpi.softPwmWrite(self._servo_pins[servo_num], signal)
        wiringpi.delay(1)
            
    def moveMotor(self, servo_num, signal_pwm):
        self._actuate_Motor(servo_num, signal_pwm)
    
    # Returns Sensor in radians 
    def readSensor(self):
        deltaIn = self.servo_pos - self.servo_pwm_min
        rangeIn = self.servo_pwm_max - self.servo_pwm_min
        rangeOut = 3.1459
        return (deltaIn * rangeOut) / rangeIn, self.servo_pos*self.dt

class MPU6050Control:
    def __init__(self):
        super(MPU6050Control, self).__init__()
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
        self.dt = 0.1 #Threaded at 100ms
        self.kalman_X = Kalman()
        self.kalman_Y = Kalman()
        self._initPosition()
        self.kalman_X.setAngle(self.roll)
        self.kalman_Y.setAngle(self.pitch)
        self.kalmanAngleX = 0
        self.kalmanAngleY = 0
        
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
            
    def _initPosition(self):
        self._getAccData()
        self._getGyroData()
        self.getPlatformAngle()
    
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
    
    def _getAccData(self):
        self.acc_x = self._readData16bit("ACCEL_XOUT_H")/16384
        self.acc_y = self._readData16bit("ACCEL_YOUT_H")/16384
        self.acc_z = self._readData16bit("ACCEL_ZOUT_H")/16384
    
    def _getGyroData(self):
        self.gyro_x = self._readData16bit("GYRO_XOUT_H")/131
        self.gyro_y = self._readData16bit("GYRO_YOUT_H")/131
        self.gyro_z = self._readData16bit("GYRO_ZOUT_H")/131
    
    def kalmanFilter(self):
        #filteredData = kf_update(self.roll_list)
        return filteredData
    
    def getPlatformAngle(self):
        self.roll = math.atan2(self.acc_y, self.acc_z)
        self.pitch = math.atan(-self.acc_x/math.sqrt((self.acc_y**2)+(self.acc_z**2)))
    
    def processAngle(self):
        if((self.pitch < -90 and self.kalAngleY >90) or (self.pitch > 90 and self.kalAngleY < -90)):
            self.kalmanY.setAngle(self.pitch)
            self.kalAngleY   = self.pitch
            self.gyroYAngle  = self.pitch
        else:
            kalAngleY = kalmanY.getAngle(pitch,gyroYRate,dt)

        if(abs(kalAngleY)>90):
            self.gyro_x  = -self.gyro_x
            kalAngleX = kalmanX.getAngle(roll,gyroXRate,dt)

        self.gyroXAngle = self.gyro_x*self.dt
        self.gyroYAngle = self.gyro_y*self.dt
        
        if (self.gyroXAngle < -180) or (self.gyroXAngle > 180):
            self.gyroXAngle = kalAngleX
        if (self.gyroYAngle < -180) or (self.gyroYAngle > 180):
            self.gyroYAngle = kalAngleY
        
        return kalAngleX, kalAngleY
        
class PiCameraControl:
    def __init__(self, camera_resolution):
        super(PiCameraControl, self).__init__()
        camera_resolution_h, camera_resolution_w = camera_resolution
        self.camera = Picamera()
        self._initCamera()
        self.image = np.empty(camera_resolution_h, camera_resolution_w)
        
    def _initCamera(self):
        try:
            self.camera.start_preview()
            time.sleep(5)
            self.camera.stop_preview()
        except AttributeError:
            print("Could not start the camera, please check the connections. Exiting.\n")
            print("Tip:\t You may need to initialize the camera using raspi-config.\n")
            exit(0)
        finally:
            self.camera.close()
    # todo: Verify capture images and feed to network.
    def captureImage(self):
        return self.camera.capture(self.image, 'rgb')
        