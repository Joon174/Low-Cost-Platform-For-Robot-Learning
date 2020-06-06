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
    def __init__(self, servo_control_pins, camera_resolution):
        super(Agent, self).__init__(servo_control_pins, camera_resolution)
        self.model = 0
        self.robot = RobotPlatform.__init__(self, servo_control_pins, camera_resolution)
        self.done = False
    def _initRobotPlatform(self):
        self._init_servos()
        self._init_MPU()
        self._init_Camera()
    
    def loadModel(path, file_name):
        model_path = os.path.join(os.getcwd(), path, file_name)    
        self.model = torch.load(model_path)
    
    def convert(self):
        pass
    
    # Used for testing API for agent and platform
    def evaluate(self):
        assert self.model == 0, "No Architecture found on Agent."
        rewards = []
        self.robot.reset()
        while not done:
            position = self.robot.readSensor("S3003")
            action = self.model(position)
            signal = convert(action)
            next_state, reward, done,_ = self.robot.step(servo_pin, signal)
            rewards.append(reward)
        
        return rewards