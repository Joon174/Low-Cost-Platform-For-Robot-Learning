## @package user_interface.py
#
import torch
#from robot_platform import RobotPlatform
from include.robot_platform import RobotPlatform
from include.exampleAgents import PPOAgent

#---------------------------
#      Main Function
#---------------------------

# Init pins of the model
servo_pin_list = [1]

# Init Model
agent = PPOAgent()
env = RobotPlatform(servo_pin_list)
agent.defineEnv(env)
directory = r"modelWeights"
file_name = r"test_weights_PPO.pt"
agent.loadWeights(directory, file_name)
