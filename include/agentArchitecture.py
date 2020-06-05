## @package agentArchitecture.py
#  @brief Contains Agent Architecture for the pipeline proof of concept
#  This package contains all agent architectures for testing the platform. They are architectures which meet the performance baselines. 
#  More details.

import math
import random

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.distributions import Normal
from collections import deque

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
        # Create three separate values for the thing to choose.
        self.num_actions = 7*env.action_space.shape[0]
        self.epsilon_start = 1.0
        self.epsilon_final = 0.1
        self.epsilon_decay = 1000
        self.layers = nn.Sequential(
            nn.Linear(self.input_dim[0], 128),
            nn.ReLU(),
            nn.Linear(128, 128),
            nn.ReLU(),
            nn.Linear(128, self.num_actions)
        )
    
    def epsilon_greed_strat(self, time_step):
        return self.epsilon_final + (self.epsilon_start + self.epsilon_final) * math.exp(-1. * time_step / self.epsilon_decay)

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
            action = self.evaluate(state)
        else:
            action = random.randrange(self.num_actions)
        return action

    def evaluate(self, state):
        qval = self.get_qvals(state)
        return qval.max(1)[1].detach()

    def get_qvals(self, state):
        # Pass the state image into our network:
        with torch.no_grad():
            state_t = torch.cuda.FloatTensor(np.float32(state)).unsqueeze(0)
            return self.forward(state_t)

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
    
    loss = F.mse_loss(qvals, expected_qvals.detach().cuda())

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    return loss

## Actor Crtiic
#  A Linear Model with the Actor-Crtitc (A2C) architecture. This model can be modified using the XX tool
#  @author: Joon You Tan
#  @date: 20-May-2020
#  @note The following is the default architecture for this agent:
#  @note Layer 1: Linear, (in_channels = environment = 128) -> ReLU
#  @note Layer 2: Linear, (in_channels = 128, out_channels = 128)
#  @note Layer 3: Linear, (in_channels = 128, out_channels = number of actions available for agent)
#  @note The actions for this model are evaluated using the Epsilon Greedy Strategy

def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.normal_(m.weight, mean=0., std=0.1)
        nn.init.constant_(m.bias, 0.1)

def compute_gae(next_value, rewards, masks, values, gamma=0.99, tau=0.95):
    values = values + [next_value]
    gae = 0
    returns = []
    for step in reversed(range(len(rewards))):
        delta = rewards[step] + gamma * values[step + 1] * masks[step] - values[step]
        gae = delta + gamma * tau * masks[step] * gae
        returns.insert(0, gae + values[step])
    return returns

## Actor Crtiic
#  A Linear Model with the Actor-Crtitc (A2C) architecture. This model can be modified using the XX tool
#  @author: Joon You Tan
#  @date: 20-May-2020
#  @note The following is the default architecture for this agent:
#  @note Layer 1: Linear, (in_channels = environment = 128) -> ReLU
#  @note Layer 2: Linear, (in_channels = 128, out_channels = 128)
#  @note Layer 3: Linear, (in_channels = 128, out_channels = number of actions available for agent)
#  @note The actions for this model are evaluated using the Epsilon Greedy Strategy

class ActorCritic(nn.Module):
    def __init__(self, env, hidden_size=256, std=0.0):
        super(ActorCritic, self).__init__()
        num_inputs = env.observation_space.shape[0]
        num_outputs = env.action_space.shape[0]
        self.critic = nn.Sequential(
            nn.Linear(num_inputs, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, 1)
        )
        
        self.actor = nn.Sequential(
            nn.Linear(num_inputs, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, num_outputs)
        )
        self.log_std = nn.Parameter(torch.ones(1, num_outputs) * std)
        self.apply(init_weights)
        self.optimizer = 0

    def forward(self, x):
        value = self.critic(x)
        mu    = self.actor(x)
        std   = self.log_std.exp().expand_as(mu)
        dist  = Normal(mu, std)
        return dist, value
    
    def getOptimizer(self, optimizer):
        self.optimizer = optimizer

    def ppo_iter(self, mini_batch_size, states, actions, log_probs, returns, advantage):
        batch_size = states.size(0)
        for _ in range(batch_size // mini_batch_size):
            rand_ids = np.random.randint(0, batch_size, mini_batch_size)
            yield states[rand_ids, :], actions[rand_ids, :], log_probs[rand_ids, :], returns[rand_ids, :], advantage[rand_ids, :]

    def ppo_update(self, ppo_epochs, mini_batch_size, states, actions, log_probs, returns, advantages, clip_param=0.4):
        for _ in range(ppo_epochs):
            for state, action, old_log_probs, return_, advantage in self.ppo_iter(mini_batch_size, states, actions, log_probs, returns, advantages):
                dist, value = self.forward(state)
                entropy = dist.entropy().mean()
                new_log_probs = dist.log_prob(action)

                ratio = (new_log_probs - old_log_probs).exp()
                surr1 = ratio * advantage
                surr2 = torch.clamp(ratio, 1.0 - clip_param, 1.0 + clip_param) * advantage

                actor_loss  = - torch.min(surr1, surr2).mean()
                critic_loss = (return_ - value).pow(2).mean()

                loss = 0.5 * critic_loss + actor_loss - 0.001 * entropy

                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
            