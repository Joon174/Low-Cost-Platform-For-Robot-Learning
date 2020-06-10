## PCA9685_interface
import wiringpi
import time

class PCA9685():
    def __init__(self, address=0x40, pwm_freq=50):
        super(PCA9685, self).__init__()
        self.address = address
        self.freq = 0
        self.registers = {"MODE1": 0x00,
                          "PRESCALE": 0xFE,
                          "LED0_ON_L": 0x06,
                          "LED0_ON_H": 0x07,
                          "LED0_OFF_L": 0x08,
                          "LED0_OFF_H": 0x09,
                          "LED_ALL_ON":0xFA,
                          "PIN_ALL": 0x0F
              }
        self.device = self._initConnection()
        self._setupDevice()
        self._setPWMFreq(pwm_freq)
        
    # initConnection
    #  Checks for a return from the MPU6050 in the I2C bus. Should there be no gyroscope
    #  found, the class will assert an error and exit the program.   
    def _initConnection(self):
        try:
            device = wiringpi.wiringPiI2CSetup(self.address)
            print("Successfully conneced to PCA9685 IC Chip.\n")
            return device
        except AttributeError:
            print("Failed to connect to device. Please check the connection.\n")
            print("Tip:\t You may need to initialize the I2C bus using raspi-config.\n")
            exit(0)
    
    def _setupDevice(self):
        settings = wiringpi.wiringPiI2CReadReg8(self.device, self.registers["MODE1"]) & 0x7F
        auto_increment = settings | 0x20
        wiringpi.wiringPiI2CWriteReg8(self.device, self.registers["MODE1"], auto_increment)
    
    def _setPWMFreq(self, freq):
        self.freq = (1000 if freq>1000 else freq if freq<400 else 400)
        prescale = int(25000000/(4096*freq) - 0.5)
        settings = wiringpi.wiringPiI2CReadReg8(self.device, self.registers["MODE1"]) & 0x7F
        sleep = settings | 0x10
        wake = settings & 0xEF
        restart = wake | 0x80
        wiringpi.wiringPiI2CWriteReg8(self.device, self.registers["MODE1"], sleep)
        wiringpi.wiringPiI2CWriteReg8(self.device, self.registers["PRESCALE"], prescale)
        wiringpi.wiringPiI2CWriteReg8(self.device, self.registers["MODE1"], wake)
        time.sleep(0.001)
        wiringpi.wiringPiI2CWriteReg8(self.device, self.registers["MODE1"], restart)
    
    def _triggerPulse(self, channel, on, off):
        wiringpi.wiringPiI2CWriteReg8(self.device, self.registers["LED0_ON_L"]+4*channel, on & 0xFF)
        wiringpi.wiringPiI2CWriteReg8(self.device, self.registers["LED0_ON_H"]+4*channel, on >> 8)
        wiringpi.wiringPiI2CWriteReg8(self.device, self.registers["LED0_OFF_L"]+4*channel, off & 0xFF)
        wiringpi.wiringPiI2CWriteReg8(self.device, self.registers["LED0_OFF_H"]+4*channel, off >> 8)
    
    def servo_set_angle(self, channel, pulse):
        analog_value = int(float(pulse) / 1000000 * self.freq * 4096)
        self._triggerPulse(channel, 0, analog_value)
    