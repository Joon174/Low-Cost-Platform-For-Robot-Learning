# !/usr/bin/env/python3
## RobotPlatform.py

# import packages for API
import numpy as np
import wiringpi
from picamera import PiCamera

# import all API packages for kernel operation:
from include.control_interface import ServoControl, MPU6050Control
from include.event_thread_handler import ThreadEvent

class TrajectoryHandler:
    def __init__(self, trajectory_list):
        self._trajectory_list = trajectory_list
        self.max_size = len(self._trajectory_list)
        self._idx = 0
        
    def _get_next_target(self):
        if (self._idx + 1) <= self.max_size:
            state =  self._trajectory_list[self._idx+1]
        else:
            state = self._trajectory_list[self._idx]
        return state

class RobotPlatform(ServoControl, MPU6050Control, ThreadEvent, TrajectoryHandler):
    def __init__(self, servo_output_pins):
        wiringpi.wiringPiSetup()
        test = [1, 2]
        self.servo = ServoControl(servo_output_pins)
        self.mpu6050 = MPU6050Control()
        self.trajectory = TrajectoryHandler(test)
        self.sensors = {"S3003", self.servo,
                        "MPU6050", self.mpu6050}
        self.observation_space = self.step(1, 1750)
        self.action_space = len(servo_output_pins)
        self.done = False
        
    def getData(self, sensorName):
        return self.sensors[sensorName].readSensor()
    
    def addTrajectory(self, trajectory_list):
        self.trajectory = TrajectoryHandler(trajectory_list)
        
    def step(self, servo_idx, pwm_signal):
        if False:
            #todo: Fix the logic for observation_space of the robot
            self.servo.moveMotor(servo_idx, pwm_signal)
            servo_pos, _ = self.getData("S3003")
            body_pos = self.getData("MPU6050")
            result = np.concatenate([servo_pos], [body_pos])
            
        if True:
            servo_pos, servo_vel = self.servo.readSensor()
            result = np.concatenate([servo_pos], [self.trajectory._get_next_target()], [servo_vel])
        
        return result
    
    def reset(self):
        self.servo._init_servo_pos()
        self.mpu6050._init_pos()
        