# Low-Cost-Platform-For-Robot-Learning
This repository contains the development and integration of the interface scripts between the agent and the robotic platform.

## About
Reinforcement Learning (RL) is an emerging field for controlling robots in an advance manner. Although progress has been made in the field, the validation of RL algotihms becomes difficult due to the cost of the robotic hardware. As such, a low-cost platform is designed to ease the complexity for using expensive equipment and introduce an interface which is user friendly. The aim is to develop a low-cost platform targeted towards researchers and students for reinforcement learning research. 

## Prerequisites
Please note that the projcet requires the following packages to run:
1. [Pytorch ver 1.4 (stable) and above](https://pytorch.org/)
2. [Mujoco_py (wrapper)](https://github.com/openai/mujoco-py) and [Mujoco (core)](https://www.roboti.us/license.html)
3. [OpenAI Gym ver 14.0 and above](https://github.com/openai/gym)
4. [WiringPi-Python](https://github.com/WiringPi/WiringPi-Python)
5. [Servoblaster](https://github.com/richardghirst/PiBits/tree/master/ServoBlaster)

## Documentation
### Application Programming Interface (API)
Refer to this [link](doc/index.html) for full description of the python package and API procedure

### Assembly Instructions
Refer to this [link](doc/assembly.pdf) for full instructions on the assembly of the platform.

## Getting Started
Download the repository with the following command:
```
git clone https://github.com/Joon174/Low-Cost-Platform-For-Robot-Learning
```
Sample the scripts in the include file into your working folder and import robot_platform.py to get started.

## Participants
**Joon You Tan** - *Mechatronics Engineering Student - Project Member*  
**Prof. Dana Kulic** - *Professor, Department of Electrical and Computer Systems Engineering - Supervisor*
