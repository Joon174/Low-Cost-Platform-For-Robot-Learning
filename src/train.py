## @package train.py
#  @brief Contains a PPO Agent to train an agent to learn to follow a certain trajectory.

import gym
import numpy as np
from gym import wrappers
import scipy.signal
from datetime import datetime
import os
import argparse
import signal
from time import sleep
import matplotlib.pyplot as plt

## Create an instance of the class pls
