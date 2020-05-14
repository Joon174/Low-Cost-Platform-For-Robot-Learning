## @package agent_bridge.py

from servo_interface import RobotPlatform

class Agent(RobotPlatform):
    def __init__(self, model):
        self.model = model
        
    def test(self):
        # Init Pos signal is defined as such:
        init_pos_signal = 9
        