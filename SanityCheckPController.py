import gym
import numpy as np
import torch
import matplotlib.pyplot as plt
from gym.envs.registration import register
from common.multiprocessing_env import SubprocVecEnv

register(
    id='ProofOfConceptModel-v0', 
    entry_point='src.env.envRegister:ProofOfConceptModel',
    reward_threshold=4800.0,
    )

env = gym.make('ProofOfConceptModel-v0')
servo_range_radians = (0.056, -0.84)
total_time_steps = 200 # For 5 second sample
front = np.linspace(servo_range_radians[0], servo_range_radians[1], total_time_steps)
back = np.linspace(servo_range_radians[1], servo_range_radians[0], total_time_steps)
trajectory_angles = np.concatenate([front, back, front, back, front, back])
env.add_trajectory(trajectory_angles)

P_gain = 5

env.reset()
action = env.action_space.sample()
done = False
while True:
    rewards = []
    while not done:
        env.render()
        _, reward, done, _ = env.step(action)
        action = reward*P_gain
        rewards.append(reward)
    env.reset()
    done = False
    plt.plot(rewards)
    plt.show()