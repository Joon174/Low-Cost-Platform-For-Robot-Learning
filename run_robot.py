#!/usr/bin/python3
## @package run_robot.py
#  @brief Script for testing the software to hardware API.
#  run_robot is an example script of how the LowCostPlatform will be used for education and testing purposes.

# Import relevant packages for processing
import torch
import numpy as np
from include.robot_platform import RobotPlatform
from include.exampleAgents import PPOAgent

# Initialise the servos according to the servoblaster
servo_pin_list = [12]

# Reinitiate the sequence of the trajectory for the Agent
servo_range_radians = (0.349, -0.175)
total_time_steps = 200
front = np.linspace(servo_range_radians[0], servo_range_radians[1], total_time_steps)
back = np.linspace(servo_range_radians[1], servo_range_radians[0], total_time_steps)
test_traj = np.concatenate([front, back, front, back, front, back])

# Initiate the model for testing purposes
agent = PPOAgent()
env = RobotPlatform(servo_pin_list, test_traj)
agent.defineEnv(env)
directory = r"modelWeights"
file_name = r"proof_of_concept_PPO_weights.pt"
agent.loadWeights(directory, file_name)

# Test Agent with the given current weights:
agent.test_env(env, False, False)