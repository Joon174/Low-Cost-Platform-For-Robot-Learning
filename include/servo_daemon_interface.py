## PCA9685_interface
import os

servo_minPulse = [0]*41
servo_maxPulse = [0]*41
servo_minAngle = [0]*41
servo_maxAngle = [0]*41

def servo_set(servoPin, servoOutput):
    os.system("echo " + "P1-" + str(servoPin) + "=" + servoOutput + " > /dev/servoblaster")

def servo_map(value, oldMin, oldMax, newMin, newMax):
    return ((value-oldMin)*(newMax-newMin)/(oldMax-oldMin)+newMin) / 11

def servo_configure(servoPin, minPulse=1000, maxPulse=2000, minAngle=-90, maxAngle=90):
    servo_minPulse[servoPin] = minPulse
    servo_maxPulse[servoPin] = maxPulse
    servo_minAngle[servoPin] = minAngle
    servo_maxAngle[servoPin] = maxAngle

def servo_set_angle(servoPin, servoAngle): 
    pwm_sig = servo_map(servoAngle, servo_minAngle[servoPin], servo_maxAngle[servoPin], servo_minPulse[servoPin], servo_maxPulse[servoPin])
    os.system("echo " + "P1-" + str(servoPin) + "=" + str(pwm_sig) + " > /dev/servoblaster")