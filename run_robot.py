## @package user_interface.py
#
import torch
import numpy as np
#from robot_platform import RobotPlatform
from include.robot_platform import RobotPlatform
from include.exampleAgents import PPOAgent

#---------------------------
#      Main Function
#---------------------------

# Init pins of the model
servo_pin_list = [12]
min_new_rad = ((0)*(-0.84-0.056)/(25+10)+0.056)
max_new_rad = ((35)*(-0.84-0.056)/(25+10)+0.056)
servo_range_radians = (min_new_rad, max_new_rad)
total_time_steps = 200 # For 10 second sample
front = np.linspace(servo_range_radians[0], servo_range_radians[1], total_time_steps)
back = np.linspace(servo_range_radians[1], servo_range_radians[0], total_time_steps)
test_traj = np.concatenate([front, back, front, back, front, back])

# Init Model
agent = PPOAgent()
env = RobotPlatform(servo_pin_list, test_traj)
agent.defineEnv(env)
directory = r"modelWeights"
file_name = r"proof_of_concept_PPO_weights.pt"
agent.loadWeights(directory, file_name)

# Test Agent with the given current weights:
agent.test_env(env, False, False)
