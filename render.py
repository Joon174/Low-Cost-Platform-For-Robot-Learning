## @package render.py
#  @brief Used to test if the algorithm can render the environment well.

import gym
import numpy as np
import math
from gym.envs.registration import register

import torch
import torch.optim as optim
from agent import Agent

# Register the environments for agent
# gym.envs.register(id='Queen-v1', entry_point='env.envRegister:QueenV1', max_episode_steps=1000, reward_threshold=4800.0)
register(
	id='ProofOfConceptModel-v0', 
	entry_point='src.env.envRegister:ProofOfConceptModel', 
	max_episode_steps=1000, 
	reward_threshold=4800.0,
	)

# Create trajectory joint angles (radians) for trainng
# Note that the change in time (dt) is 0.05
servo_range_radians = (0.785398, -0.698132)
total_time_steps = 200 # For 10 second sample
trajectory_angles = np.linspace(servo_range_radians[0], servo_range_radians[1], total_time_steps)

# ==================================================================
# 							Main Function
# ==================================================================
env = gym.make('ProofOfConceptModel-v0')
env.add_trajectory(trajectory_angles)

sample_agent = Agent(env)

sample_agent.train()
