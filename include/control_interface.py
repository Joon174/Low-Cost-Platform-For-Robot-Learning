## @package control_interface
#  @brief API linking the agent's control signals to the raspberry pi on a interface layer.
#  Contains the all relevant controls needed for the robot to actuate and walk. Should
#  further sensors or controllers be added to the system, they can be added here to be
#  used with the Agent.
#  @note Each new control layer should be designed as a parent class when added to this
#  script.

# Packages for processing
import numpy as np
import math
import cv2
import time

# Packages for kernel operations
import wiringpi
from picamera import PiCamera
from PIL import Image
from include.servo_daemon_interface import *
from include.i2c_handler import PCA9685
from include.filters import Kalman

## ServoControl
#  Parent class used to control the servos on the platform. The class is instantiated with
#  the control pins for the relevant servos used. Once the pins have been selected, the
#  interface will reset the position of the servo back to 0 degrees. Customisations of servo
#  characteristics can be implemented into the sytem. 
class ServoControl:
    def __init__(self, servo_pins_list):
    ## Constructor
    #  Upon constructing the class, the ServoControl class will set the relevant GPIO pins
    #  for servo control. Then initiate them to the starting position of 0.
        super(ServoControl, self).__init__()
        self._servo_pins = servo_pins_list
        self.servo_pos_before = 0
        self.servo_pos_after = 0
        self.servo_pwm_min = 550
        self.servo_pwm_max = 3000
        self._init_pos_angle = 5
        self._init_servos()
        self.dt = 0.01
        self.mujoco_range = [-5, 5]
        self.pca = PCA9685()

    ## init_servos
    #  Initiates the GPIO pins to the relevant servos used in the platform currently.
    def _init_servos(self):
        for i in range(len(self._servo_pins)):
            servo_configure(self._servo_pins[i], self.servo_pwm_min, self.servo_pwm_max, -90, 90)
        self._init_servo_pos()
    
    ## init_servo_pos
    #  Sets the servo position back to the initial state. Defaults to 0 degrees (1500us).   
    def _init_servo_pos(self):
        for i in range(len(self._servo_pins)):
            servo_set_angle(self._servo_pins[i], self._init_pos_angle)
    
    ## convert_to_pwm
    #  Maps the agent's actions to the pwm control signals
    #  @param control_sig Action evaluated by the agent, relevant to the training.
    def _convert_to_pwm(self, control_sig):
        oldMin = self.mujoco_range[0]
        oldMax = self.mujoco_range[1]
        newMin = -10
        newMax = 20
        return ((control_sig-oldMin)*(newMax-newMin)/(oldMax-oldMin)+newMin)
    
    ## actuate_motor
    #  Sends the relevant commands to the daemon process to actuate PWMs on a physical
    #  layer.
    #  @param servo_num The index of the corresponding servo to be controlled in the
    #  list ServoControl was instantiated with
    #  @param control_sig The control signal provided by the agent. (Dependent on training
    #  of user).
    def _actuate_Motor(self, servo_num, control_sig):
        signal = self._convert_to_pwm(control_sig)
        analog = servo_map(signal, 0, 180, self.servo_pwm_min, self.servo_pwm_max)
        self.pca.servo_set_angle(servo_num, signal)
        #servo_set_angle(self._servo_pins[servo_num], signal)  
           
    def moveMotor(self, servo_num, signal_pwm):
        self._actuate_Motor(servo_num, signal_pwm)
    
    ## readSensor
    #  Returns the servo's angle in radians 
    def readSensor(self):
        deltaIn = self.servo_pos_after - self.servo_pwm_min
        rangeIn = self.servo_pwm_max - self.servo_pwm_min
        rangeOut = 3.1459
        vel = (self.servo_pos_after - self.servo_pos_before)*self.dt
        self.servo_pos_before = self.servo_pos_after
        return (deltaIn * rangeOut) / rangeIn, vel

## MPU6050Control
#  Parent class used to read the orientation of the device. Originally created to be used for 
#  walking but due to the lack of resources remains untested on the final control algorithm.
#  Class has been unit tested on a higher level to function fine. 
class MPU6050Control:
    def __init__(self):
    ## Constructor
    #  Upon constructing the class, MPU6050Control will source out a MPU6050 in the I2C bus
    #  Should there be an instance where the gyroscope is not found during initialization,
    #  an error is asserted an halts the program. All registers and values in this class are
    #  relative to the MPU6050. Any other orientation-measuring devices with different
    #  properties or communication channel will have to be implemented separately. Kalman
    #  filters are used in this control class.
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
        self.dt = 0.01 #Threaded at 100ms
        self.kalman_X = Kalman()
        self.kalman_Y = Kalman()
        self._initPosition()
        self.kalman_X.setAngle(self.roll)
        self.kalman_Y.setAngle(self.pitch)
        self.kalAngleX = 0
        self.kalAngleY = 0

    ## initConnection
    #  Checks for a return from the MPU6050 in the I2C bus. Should there be no gyroscope
    #  found, the class will assert an error and exit the program.   
    def _initConnection(self):
        try:
            device = wiringpi.wiringPiI2CSetup(self.address)
            print("Successfully conneced to MPU6050 Sensor.\n")
            return device
        except AttributeError:
            print("Failed to connect to device. Please check the connection.\n")
            print("Tip:\t You may need to initialize the I2C bus using raspi-config.\n")
            exit(0)
    
    ## initMPU
    #  Sends I2C command to configure the MPU6050 accoridng to specifications. Enables
    #  feedback of the sensor to read gyroscope and accelerometer messages.
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

    ## initPosition
    #  Gets the current position of the platform during initialization for localization.     
    def _initPosition(self):
        self._getAccData()
        self._getGyroData()
        self.getPlatformAngle()
    
    ## readData8bit 
    #  Reads the given register name for a 8-bit resolution.
    #  @param register_name string input of the relevant register to be read.
    def _readData8bit(self, register_name):
        high = wiringpi.wiringPiI2CReadReg8(self.device, self.registers[register_name])
        low = wiringpi.wiringPiI2CReadReg8(self.device, self.registers[register_name]+1)
        value = ((high << 8) | low) 
        return value if value > 32786 else value - 65546

    ## readData16bit 
    #  Reads the given register name for a 16-bit resolution.
    #  @param register_name string input of the relevant register to be read.   
    def _readData16bit(self, register_name):
        high = wiringpi.wiringPiI2CReadReg16(self.device, self.registers[register_name])
        low = wiringpi.wiringPiI2CReadReg16(self.device, self.registers[register_name]+1)
        value = ((high << 8) | low) 
        return value if value > 32786 else value - 65546
    
    ## writedData8bit 
    #  Writes to the given register name of 8-bit resolution.
    #  @param register_name string input of the relevant register to be written.   
    def _writeData8bit(self, register_name, data):
        return wiringpi.wiringPiI2CWriteReg8(self.device, self.registers[register_name], data)
    
    ## writedData16bit 
    #  Writes to the given register name of 16-bit resolution.
    #  @param register_name string input of the relevant register to be written.  
    def _writeData16bit(self, register_name, data):
        return wiringpi.wiringPiI2CWriteReg16(self.device, self.registers[register_name], data)
    
    ## getAccData 
    #  Reads the accelerometer values and returns the messages converted to their raw states.   
    def _getAccData(self):
        self.acc_x = self._readData16bit("ACCEL_XOUT_H")/16384
        self.acc_y = self._readData16bit("ACCEL_YOUT_H")/16384
        self.acc_z = self._readData16bit("ACCEL_ZOUT_H")/16384
    
    ## getGyrocData 
    #  Reads the gyroscope values and returns the messages converted to their raw states. 
    def _getGyroData(self):
        self.gyro_x = self._readData16bit("GYRO_XOUT_H")/131
        self.gyro_y = self._readData16bit("GYRO_YOUT_H")/131
        self.gyro_z = self._readData16bit("GYRO_ZOUT_H")/131
    
    ## kalmanFilter 
    #  Applies the kalman filter to the roll angles observed by the platform.
    def kalmanFilter(self):
        #filteredData = kf_update(self.roll_list)
        return filteredData
    
    ## getPlatformAngle 
    #  Converts the accelerometer and gyroscope values to valid radian form.
    def getPlatformAngle(self):
        self.roll = math.atan2(self.acc_y, self.acc_z)
        self.pitch = math.atan(-self.acc_x/math.sqrt((self.acc_y**2)+(self.acc_z**2)))
    
    ## kf_update
    #  Updates the angles as according to the structure of the Kalman Filter.
    def kf_update(self):
        self._initPosition()
        if((self.pitch < -90 and self.kalAngleY >90) or (self.pitch > 90 and self.kalAngleY < -90)):
            self.kalman_Y.setAngle(self.pitch)
            self.kalAngleY   = self.pitch
            self.gyroYAngle  = self.pitch
        else:
            self.kalAngleY = self.kalman_Y.getAngle(self.pitch,self.gyro_y,self.dt)

        if(abs(self.kalAngleY)>90):
            self.gyro_x  = -self.gyro_x
            self.kalAngleX = self.kalman_X.getAngle(self.roll,self.gyro_x,self.dt)

        self.gyroXAngle = self.gyro_x*self.dt
        self.gyroYAngle = self.gyro_y*self.dt
        
        if (self.gyroXAngle < -180) or (self.gyroXAngle > 180):
            self.gyroXAngle = self.kalAngleX
        if (self.gyroYAngle < -180) or (self.gyroYAngle > 180):
            self.gyroYAngle = self.kalAngleY
        
        return self.kalAngleX, self.kalAngleY
        
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