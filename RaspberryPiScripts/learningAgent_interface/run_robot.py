## @package user_interface.py
#
import os
import torch
from control_interface import RobotPlatform
from agent_model import Agent

#---------------------------
#      Main Function
#---------------------------
 
# init the robot legs Please refer to the wiringpi GPIO list for all pin allocations
pinList = [1, 2, 3, 4, 5, 6]

# Cannot load file as "include" is a package in the local repo for training the code.
model = RobotPlatform(pinList)

while True:
    gyro_x, gyro_y, gyro_z = model.getGyroData()
    print("Gyro values are x:{},\ty:{},\tz:{}\r".format(gyro_x, gyro_y, gyro_z))