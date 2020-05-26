## @package agent_model.py

# pytorch package used to connect with wiringPi
import torch 
import torchvision
import torchvision.transforms as transforms

import torch.nn as nn
import torch.nn.functional as F

# import custom interface script for the agent
from robot_platform import RobotPlatform
#from environment import KernelAPI

class Agent(RobotPlatform):
    def __init__(self, model):
        super(Agent, self).__init__()
        RobotPlatform.__init__(self, servo_control_pins)
        self.model = nn.Sequential(nn.Linear(4, 128),
                                   nn.ReLU(),
                                   nn.Linear(128, 128),
                                   nn.ReLU(),
                                   nn.Linear(128, 1)
                                   )
    def _initRobotPlatform(self):
        self._init_servos()
        self._init_MPU()
        self._init_Camera()
    
    def loadModel(path, file_name):
        model_path = os.path.join(os.getcwd(), path, file_name)    
        model = torch.load(model_path)
        return model
    
    def train(self):
        return
    
    def validate(self):
        return
        
    def test(self):
        # Init Pos signal is defined as such:
        init_pos_signal = 9
