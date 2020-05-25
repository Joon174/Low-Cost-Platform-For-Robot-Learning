#!/usr/bin/python3
## @package render.py
#  @brief Used to test if the algorithm can render the environment and train properly.
#  Render.py is a script used during TDD for training simple agents with in order to port the weights to the 
#  Raspberry Pi Model 4 for unit testing. Instances of DQN and PPO agents are present to illustrate the 
#  flexibilty of the program on differen types of agent architectures.

import gym
import numpy as np
from gym.envs.registration import register
from common.multiprocessing_env import SubprocVecEnv
from include.exampleAgents import DQNAgent, PPOAgent

## make_env
#  A simple function utilising OpenAi's Baseline code for creating multiple environments for multiprocessing.
#  (view common file for link to original folder)
def make_env(env_name, trajectory_angles):
	def _thunk():
		env = gym.make(env_name)
		env.add_trajectory(trajectory_angles)
		return env
	return _thunk

## Environment Registration
#  To register custom environments to the OpenAI Gym's package, the registration kit from the Gym package is utilised. 
#  Refer to the documentation of OpenAI Gym's git repository for information on the process and parameters used for initialisation.

# Set to true to use the full Robotic Platform
if False:
	register(id='Queen-v1',
	 	entry_point='env.envRegister:QueenV1', 
		max_episode_steps=1000, 
		reward_threshold=4800.0
		)
# Set to true to test on a single leg of the Robotic Platform
if True:
	register(
		id='ProofOfConceptModel-v0', 
		entry_point='src.env.envRegister:ProofOfConceptModel', 
		max_episode_steps=1000, 
		reward_threshold=4800.0,
		)

# Create trajectory joint angles (radians) for trainng
# Note that the change in time (dt) is 0.05
servo_range_radians = (-0.5, -1.5)
total_time_steps = 20 # For 5 second sample
front = np.linspace(servo_range_radians[0], servo_range_radians[1], total_time_steps)
back = np.linspace(servo_range_radians[1], servo_range_radians[0], total_time_steps)
trajectory_angles = np.concatenate([front, back, front, back, front, back])

# ==================================================================
# 							Main Function
# ==================================================================
# Main guard for multiprocessing environment
if __name__ == '__main__':
	num_envs = 16
	envs = [make_env('ProofOfConceptModel-v0', trajectory_angles) for i in range(num_envs)]
	envs = SubprocVecEnv(envs)

	env = gym.make('ProofOfConceptModel-v0')
	env.add_trajectory(trajectory_angles)

	# Set to true to run the DQN Example
	if True:
		sample_agent = DQNAgent(env)
		sample_agent.train()
		
	# Set to true to run the DQN Example
	if False:
		sample_agent = PPOAgent(envs, env)
		sample_agent.train()