import os #needed to run the Servo Blaster commands
servo_minPulse = [0]*41 #crude way of "initialising" the list
                         #41 as there is only 40 output pins
servo_maxPulse = [0]*41
servo_minAngle = [0]*41
servo_maxAngle = [0]*41

def servo_set(servoPin, servoOutput, servoPinType="", servoHeader=0):
    if (servoPinType == "servo"): #If we should use the servo numbers defined by Servo Blaster.
        os.system("echo " + str(servoPin) + "=" + servoOutput + " > /dev/servoblaster")
        #print("echo " + str(servoPin) + "=" + servoOutput + " > /dev/servoblaster") #For debugging
        
    elif (servoPinType == "header"): #If we should use physical pin number on a different header
        os.system("echo " + "P" + str(servoHeader) + "-" + str(servoPin) + "=" + servoOutput + " > /dev/servoblaster")
        #print("echo " + "P" + str(servoHeader) + "-" + str(servoPin) + "=" + servoOutput + " > /dev/servoblaster")
        
    else: #We use the physical pin number on header one by default
        os.system("echo " + "P1-" + str(servoPin) + "=" + servoOutput + " > /dev/servoblaster")
        #print("echo " + "P1-" + str(servoPin) + "=" + servoOutput + " > /dev/servoblaster")

def servo_map(value, oldMin, oldMax, newMin, newMax):
    return ((value-oldMin)*(newMax-newMin)/(oldMax-oldMin)+newMin) / 10

def servo_configure(servoPin, minPulse, maxPulse, minAngle, maxAngle):
    if minPulse is not None:
        servo_minPulse[servoPin] = minPulse
    elif (servo_minPulse[servoPin] == 0):
        servo_minPulse[servoPin] = 1000
    
    if maxPulse is not None:
        servo_maxPulse[servoPin] = maxPulse
    elif (servo_maxPulse[servoPin] == 0):
        servo_maxPulse[servoPin] = 2000
    
    if minAngle is not None:
        servo_minAngle[servoPin] = minAngle
    elif (servo_minAngle[servoPin] == 0):
        servo_minAngle[servoPin] = 0
    
    if maxAngle is not None:
        servo_maxAngle[servoPin] = maxAngle
    elif (servo_maxAngle[servoPin] == 0):
        servo_maxAngle[servoPin] = 100

def servo_set_angle(servoPin, servoAngle): 
    pwm_sig = servo_map(servoAngle, servo_minAngle[servoPin], servo_maxAngle[servoPin], servo_minPulse[servoPin], servo_maxPulse[servoPin])
    os.system("echo " + "P1-" + str(servoPin) + "=" + str(pwm_sig) + " > /dev/servoblaster")