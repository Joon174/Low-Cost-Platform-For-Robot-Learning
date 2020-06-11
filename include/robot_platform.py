# !/usr/bin/env/python3
## RobotPlatform.py

# import packages for API
import time
import numpy as np
import wiringpi
from picamera import PiCamera

# import all API packages for kernel operation:
from include.control_interface import ServoControl, MPU6050Control

class TrajectoryHandler:
    def __init__(self, trajectory_list):
        super(TrajectoryHandler, self).__init__()
        self._trajectory_list = trajectory_list
        self.max_size = len(self._trajectory_list)
        self._idx = 0
        
    def _get_next_target(self):
        if (self._idx + 1) <= self.max_size:
            state =  self._trajectory_list[self._idx+1]
        else:
            state = self._trajectory_list[self._idx]
        return state
    
class RobotPlatform(ServoControl, MPU6050Control, TrajectoryHandler):
    def __init__(self, servo_output_pins, trajectory):
        wiringpi.wiringPiSetup()
        self.servo = ServoControl(servo_output_pins)
        self.mpu6050 = MPU6050Control()
        self.trajectory = TrajectoryHandler(trajectory)
        self.observation_space, _, _, _ = self.step(np.array([0]), 0)
        self.action_space = np.array(servo_output_pins)
        self.done = False
        self.accuracy
    
    def addTrajectory(self, trajectory_list):
        self.trajectory = TrajectoryHandler(trajectory_list)
        
    def step(self, action, servo_idx=0):
        #todo: Fix the logic for observation_space of the robot
        self.servo.moveMotor(servo_idx, action[0])
        servo_pos, servo_vel = self.servo.readSensor()
        position,_ = self.mpu6050.kf_update()
        self.accuracy = self.trajectory._get_next_target() - servo_pos
        rewards = -self.accuracy**2
        new_state = np.concatenate([[servo_pos], [self.trajectory._get_next_target()], [servo_vel]])
        self.trajectory._idx += 1
        self.done = self.trajectory._idx >= (np.shape(self.trajectory._trajectory_list)[0] - 1)
        info = {'Model Leg Pos (radians)': servo_pos,
                'Target Leg Pos (radians)': self.trajectory._get_next_target(),
                'Reward Accumulated': rewards
                }
        time.sleep(0.01)
        
        return new_state, rewards, self.done, info
    
    def reset(self):
        self.servo._init_servo_pos()
        self.mpu6050._initPosition()
        servo_pos,_ = self.servo.readSensor()
        servo_vel = 0
        return np.concatenate([[servo_pos], [self.trajectory._get_next_target()], [servo_vel]]) 
        