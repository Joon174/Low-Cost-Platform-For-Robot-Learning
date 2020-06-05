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
    def __init__(self, model_architecture, servo_control_pins):
        super(Agent, self).__init__()
        self.model = model_architecture
        self.robot = RobotPlatform.__init__(self, servo_control_pins)
        self.done = False
    def _initRobotPlatform(self):
        self._init_servos()
        self._init_MPU()
        self._init_Camera()
    
    def loadModel(path, file_name):
        model_path = os.path.join(os.getcwd(), path, file_name)    
        self.model = torch.load(model_path)
    
    def evaluate(self):
        self.robot.reset()
        while not done:
            position = self.robot.readSensor("S3003")
            action = self.model(position)
            next_state, reward, done, info = self.robot.step(servo_pin, signal)
