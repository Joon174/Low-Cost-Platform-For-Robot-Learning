## @package user_interface.py
#

from servo_interface import RobotPlatform
from agent_bridge import Agent

#---------------------------
#      Main Function
#---------------------------

# init the robot legs Please refer to the wiringpi GPIO list for all pin allocations
pinList = [1, 2, 3, 4, 5, 6]

model = RobotPlatform(pinList)

path = "example"
file_name = "proof_oc_concept_model.pt"

agent_architecture = loadModel(path, file_name)


