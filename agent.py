## @package: init_agent.py

import torch
import torch.optim as optim
import json
from include.exampleAgents import DQN, cal_TD_Loss

## Sample DQN Agent
#  @brief Child class created from the DQN agent architecture
class Agent:
    def __init__(self, env, batch_size=32, config_file = "include/config.txt"):  
        self.config_params = self.__getParameters(config_file)
        self.env = env
        self.__testCudeAvailable()
        self.model = DQN(self.env).cuda()
        self.target_model = DQN(self.env).cuda()

        # Training Parameters
        self.frame_idx = 0
        self.training = True
        self.rewards = 0
        self.test_rewards = list()
        self.batch_size = batch_size
        self.ep_num = 0
        self.loss = 0
        self.discount_factor = self.config_params["DQN"]["d_f"]
        self.burn_in = self.config_params["DQN"]["b_i"]
        self.save_freq = self.config_params["DQN"]["s_f"]
        self.max_episodes = self.config_params["DQN"]["m_e"]
        self.update_freq = self.config_params["DQN"]["u_f"]
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.config_params["DQN"]["lr"])
    
    def __getParameters(self, config_file):
        try: 
            with open(config_file, 'r') as json_data_file:
                return json.load(json_data_file)
        except:
            assert("Unable to locate local JSON Configuration File")

    def __testCudeAvailable(self):
        use_cuda = torch.cuda.is_available()
        try:
            device = torch.device("cuda" if use_cuda else "cpu")
            print("Current Training is attached to device: {}\r".format(device))
        except:
            assert("Pytorch cannot find any cpu or cuda chips available for training.")

    def train(self):
        state = self.env.reset()
        while self.training:
            action = self.model.get_action(state, self.frame_idx)
            next_state, reward, done, _ = self.env.step(action)
            self.model.experience.append(state, action, reward, done, next_state)
            self.rewards += reward
            state = next_state
            self.frame_idx += 1

            if(len(self.model.experience) > self.burn_in):
                self.loss = cal_TD_Loss(self.batch_size, self.model, self.target_model, self.optimizer, self.discount_factor, self.model.experience)
            
            if done:
                self.ep_num += 1
                self.test_rewards.append(self.rewards)
                state = self.env.reset()
                self.rewards = 0

                if (self.ep_num % self.save_freq == 0):
                    print("Training Episode: {} \tRewards: {} \tFrame_idx :{} \tLoss: {}\r".format(self.ep_num, self.test_rewards[-1], self.frame_idx, self.loss))

            if self.frame_idx % self.update_freq == 0:
                self.target_model.load_state_dict(self.model.state_dict())

            if self.ep_num > self.max_episodes:
                self.training = False
