## @package exampleAgents.py
#  @brief Contains Agent Architecture for the pipeline proof of concept
#  This package contains all agent architectures for testing the platform. They are architectures which meet the performance baselines. 
#  More details.

import math
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import deque
import random

## Replay Memory
#  @brief: Stores the Tuples Agent observes from the environment
#  @author: Joon You Tan
#  @date: 8-May-2020
class ReplayMemory(object):
    ## Constructor 
    #  @param memory_size Arguement to create a double-ended queue of that size.
    def __init__(self, memory_size):
        self.memory_size = memory_size
        self.replay_memory = deque(maxlen=memory_size)
  
    ## sample_batch
    #  Extracts out batch_size number of random tuples from the queue. batch_size is default to be 32.
    #  @param batch_size Number of samples to extract from the queue for processing
    def sample_batch(self, batch_size=32):
        state, action, reward, done, next_state = zip(*random.sample(self.replay_memory, batch_size))
        return state, action, reward, done, next_state
    
    ## append
    #  @param state Current environment state observed by the agent
    #  @param action Action taken by agent in that state
    #  @param reward Reward returned to agent
    #  @param done Indicator if the current episode is complete
    #  @param next_state Expected state which agent will be observing next
    def append(self, state, action, reward, done, next_state):
        self.replay_memory.append((state, action, reward, done, next_state))
        
    def __len__(self):
        return len(self.replay_memory)

## DQN
#  A Linear Model with the Deep Q-Network (DQN) architecture. This model can be modified using the XX tool
#  @author: Joon You Tan
#  @date: 8-May-2020
#  @note The following is the default architecture for this agent:
#  @note Layer 1: Linear, (in_channels = environment = 128) -> ReLU
#  @note Layer 2: Linear, (in_channels = 128, out_channels = 128)
#  @note Layer 3: Linear, (in_channels = 128, out_channels = number of actions available for agent)
#  @note The actions for this model are evaluated using the Epsilon Greedy Strategy
class DQN(nn.Module):
    ## Super Constructor
    #  @param: env The environment in which the agent will be interacting with (must be gym compatible)
    def __init__(self, env, memory_size=5000):
        super(DQN, self).__init__()
        self.experience = ReplayMemory(memory_size)
        self.input_dim = env.observation_space.shape
        self.num_actions = env.action_space.shape[0]
        self.epsilon_start = 1.0
        self.epsilon_final = 0.1
        self.epsilon_decay = 30000
        self.epsilon_greed_strat = lambda time_step: self.epsilon_final + (self.epsilon_start + self.epsilon_final) * math.exp(-1. * time_step / self.epsilon_decay)
        self.layers = nn.Sequential(
            nn.Linear(self.input_dim[0], 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, self.num_actions)
        )
    
    ## Model arguement handler
    #  @brief Passes the inputs into the agent's Linear Model
    #  @param x Input for the model. The data type will be dependent on the model architecture itself.
    def forward(self, x):
        return self.layers(x)

    ## get_action
    #  evaluates the action the agent based on Epsilon Greedy Strategy
    #  @param: state Current state of the environment the agent is observing
    #  @param: epsilon Current Epsilon value w.r.t. the Epsilon Greedy Strategy
    def get_action(self, state, epsilon):
        epsilon = self.epsilon_greed_strat(epsilon)
        if random.random() > epsilon:
            state   = torch.cuda.FloatTensor(state).unsqueeze(0)
            q_value = self.forward(state)
            action  = q_value.max(1)[1].data[0]
            action = action.cpu().numpy()
        else:
            action = random.randrange(self.num_actions)
        return action

## cal_TD_loss
#  @brief: Calculate the Temporal Difference Loss of the model.
#  @author: Joon You Tan
#  @date: 8-May-2020
def cal_TD_Loss(batch_size, model, target_model, optimizer, discount_factor, experience):
    states, actions, rewards, dones, next_states = experience.sample_batch(batch_size)
    states = torch.cuda.FloatTensor(np.float32(states))
    next_states = torch.cuda.FloatTensor(np.float32(next_states))
    rewards_t = torch.cuda.FloatTensor(rewards)
    actions_t = torch.cuda.LongTensor(actions)
    done_t = torch.cuda.FloatTensor(dones)

    qvals = model(states)
    qvals = qvals.gather(1, actions_t.unsqueeze(1)).squeeze(1)

    next_qvals = model(next_states)
    next_qval_state = target_model(next_states)
    next_qval = next_qval_state.gather(1, torch.max(next_qvals, 1)[1].unsqueeze(1)).squeeze(1)

    expected_qvals = rewards_t + discount_factor*next_qval*(1-done_t)
    
    loss = F.mse_loss(qvals, expected_qvals.detach().to(device=model.device))

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss
