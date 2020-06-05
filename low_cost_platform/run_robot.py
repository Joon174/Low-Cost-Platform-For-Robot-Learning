## @package user_interface.py
#
import os
import torch
#from robot_platform import RobotPlatform
from include.control_interface import MPU6050Control
#from agent_model import Agent

#---------------------------
#      Main Function
#---------------------------
 
# init the robot legs Please refer to the wiringpi GPIO list for all pin allocations
pinList = [1, 2, 3, 4, 5, 6]
# Cannot load file as "include" is a package in the local repo for training the code.
# todo: Create a one line in main to run the robot easily for the end user.
# todo: Verify that the platform can work with the example trained weights
# todo: Unify software architecture to port over torch model weights properly.
