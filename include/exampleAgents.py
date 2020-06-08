## @package exampleAgents.py
#  @brief Contains example agent implementations for popular algorithms: Q-Learning and Proximal Policy Optimization
#  This script serves as an example of how the Python package for the robotic platform will operate as production code
#  in the near future. To be precise, this script illustrates the structure of the software and will not contain any
#  unit testing in it. Unit testing for the python package will be done in another folder.
import os
import numpy as np
import torch
import torch.optim as optim
from include.agent import Agent
from include.agentArchitecture import DQN, ActorCritic, cal_TD_Loss, compute_gae

## DQNAgent
#  @brief Example DQN Agent; inherited properties from the Agent parent class
class DQNAgent(Agent):
    def __init__(self, env, batch_size=32, config_file="include/config.txt"):
        Agent.__init__(self)
        self.env = env
        self.config_params = self._getParameters(config_file)

        # Init Model Parameters
        self.batch_size = batch_size
        self.model = DQN(self.env).cuda()
        self.target_model = DQN(self.env).cuda()
        self.action_space = [0, 0.3, -0.3, 0.6, -0.6, 0.8, -0.8]
        self.discount_factor = self.config_params["DDQN"]["d_f"]
        self.burn_in = self.config_params["DDQN"]["b_i"]
        self.save_freq = self.config_params["DDQN"]["s_f"]
        self.max_episodes = self.config_params["DDQN"]["m_e"]
        self.update_freq = self.config_params["DDQN"]["u_f"]
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config_params["DDQN"]["lr"])
        
    def train(self):
        state = self.env.reset()
        self.time_step = 0
        while self.training:
            self.env.render()
            action = self.model.get_action(state, self.frame_idx)
            action = self.action_space[action]
            next_state, reward, done, info = self.env.step(action)
            self.model.experience.append(state, action, reward, done, next_state)
            self.rewards += reward
            state = next_state
            self.frame_idx += 1
            # self.time_step += info['Time step']
            # self.debugger.plotValues(self.time_step, [info['Model Leg Pos (radians)'], info['Target Leg Pos (radians)']])

            if(len(self.model.experience) > self.burn_in):
                self.loss = cal_TD_Loss(self.batch_size, self.model, self.target_model, self.optimizer, self.discount_factor, self.model.experience)
            
            self.checkDone(done)

            if self.frame_idx % self.update_freq == 0:
                self.target_model.load_state_dict(self.model.state_dict())

            if self.ep_num > self.max_episodes:
                self.saveWeights(directory = r"modelWeights", file_name = r"proof_of_concept_model_DQN.pt")
                self.training = False

    def checkDone(self, done):
        if done:
            self.ep_num += 1
            self.test_rewards.append(self.rewards)
            state = self.env.reset()
            self.rewards = 0
            self.time_step = 0
            # self.debugger.showPlot()

            if (self.ep_num % self.save_freq == 0):
                print("Training Episode: {} \tRewards: {} \tFrame_idx :{} \tLoss: {}\r".format(self.ep_num, self.test_rewards[-1], self.frame_idx, self.loss))

## PPOAgent
#  @brief Example PPO Agent; inherited properties from the Agent parent class
class PPOAgent(Agent):
    def __init__(self, batch_size=512, config_file="include/config.txt"):
        Agent.__init__(self)
        self.env = 0
        self.envs = 0
        self.model = 0
        self.optimizer = 0
        self.config_params = self._getParameters(config_file)
        self.max_frames = self.config_params["PPO"]["m_f"]
        self.num_steps = self.config_params["PPO"]["n_s"]
        self.threshold_reward = self.config_params["PPO"]["t_r"]
        self.ppo_epochs = self.config_params["PPO"]["p_e"]
        self.batch_size = batch_size

    def defineEnv(self, env, envs=0):
        self.env = env
        self.envs = envs
        if envs == 0:
            self.model = ActorCritic(self.env).to(self.device)
        else:
            self.model = ActorCritic(self.envs).to(self.device)
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config_params["PPO"]["l_r"])
        self.model.getOptimizer(self.optimizer)
        
    def train(self):
        state = self.envs.reset()
        early_stop = False
        while self.frame_idx < self.max_frames and not early_stop:
            log_probs = []
            values = []
            states = []
            actions = []
            rewards = []
            masks = []
            entropy = 0
            for _ in range(self.num_steps):
                state = torch.FloatTensor(state).to(self.device)
                dist, value = self.model(state)

                action = dist.sample()
                next_state, reward, done, _ = self.envs.step(action.cpu().numpy())

                log_prob = dist.log_prob(action)
                entropy += dist.entropy().mean()
                
                log_probs.append(log_prob)
                values.append(value)
                rewards.append(torch.FloatTensor(reward).to(self.device).unsqueeze(1))
                masks.append(torch.FloatTensor(1 - done).to(self.device).unsqueeze(1))
                
                states.append(state)
                actions.append(action)
                
                state = next_state
                self.frame_idx += 1
                if self.frame_idx % 1000 == 0:
                    test_reward = np.mean([self.test_env(self.env, self.model) for _ in range(10)])
                    self.test_rewards.append(test_reward)
                    if test_reward > self.threshold_reward: early_stop = True

            next_state = torch.FloatTensor(next_state).to(self.device)
            _, next_value = self.model(next_state)
            returns = compute_gae(next_value, rewards, masks, values)

            returns   = torch.cat(returns).detach()
            log_probs = torch.cat(log_probs).detach()
            values = torch.cat(values).detach()
            states = torch.cat(states)
            actions = torch.cat(actions)
            advantage = returns - values
            self.model.ppo_update(self.ppo_epochs, self.batch_size, states, actions, log_probs, returns, advantage)
        self.plotResults(self.test_rewards)
        self.saveWeights(directory=r"modelWeights", file_name=r"proof_of_concept_PPO_weights.pt", model=self.model)