## @package envRegister.py
#  @brief This file contains the interface script for mujoco_py and the end user's model to be trained
#  @date 8-May-2020
#  @author Joon You Tan
#  @version 01.05.01

# Packages used for this file:
import math
import os
import numpy as np

from gym import utils
from gym.envs.mujoco import mujoco_env

## ProofOfConceptModel
#  @brief Creates an environment for one leg of the Robotic Platform
#  The following class creates an instance of one robotic leg of the platform. The environment is
#  mainly used for unit testing for validation. The rewards of this environment are designed for
#  the accuracy following a specified trajectory input.
class ProofOfConceptModel(mujoco_env.MujocoEnv, utils.EzPickle):
    ## Constructor
    #  Instantiates variables necessary for operation; includes the permissible error between the
    #  target and current position, rewards and the index of the target in the trajectory.
    #  @param xml_file The mujoco XML file created by the end user. 
    #  @param is_healthy Ensure servo motor is within limits (does not go over and break the leg)
    #  @param terminate_when_unhealthy Prevent robot from farming rewards and not complete the task
    #  @param error_range Return true only if conditions are met (undecided as of now)
    def __init__(self, 
                healthy_reward=1.0,
                terminate_when_unhealthy=True,
                error_range=(0.05, 0.1)
                ):
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'SimpleLeg.xml')
        utils.EzPickle.__init__(self)

        self._target_leg_pos = []
        self._idx = 0
        self._healthy_reward = healthy_reward
        self._terminate_when_unhealthy = terminate_when_unhealthy
        self._error_range = error_range

        mujoco_env.MujocoEnv.__init__(self, file_path, 5)

    ## Decorators for training
    @property
    def is_healthy(self):
        min_error, max_error = self._error_range
        is_healthy = min_error < self.accuracy < max_error
        return is_healthy

    @property 
    def done(self):
        done = (not self.is_healthy
                if self._terminate_when_unhealthy
                else False)
        return done

    # Methods for calcualtions on model joint angle 
    def add_trajectory(self, list_of_angles):
        self._target_leg_pos = list_of_angles

    def _get_current_target(self):
        return self._target_leg_pos[self._idx]

    def quat_to_euler(self, quat_array):
        t_0 = +2.0 * (quat_array[3] * quat_array[0] + quat_array[1] * quat_array[2])
        t_1 = +1.0 - 2.0 * (quat_array[0] * quat_array[0] + quat_array[1] * quat_array[1])
        yaw = math.atan2(t_0, t_1)

        t_2 = +2.0 * (quat_array[3] * quat_array[1] - quat_array[2] * quat_array[0])
        t_2 = +1.0 if t_2 > +1.0 else t_2
        t_2 = -1.0 if t_2 < -1.0 else t_2
        pitch = math.asin(t_2)

        t_3 = +2.0 * (quat_array[3] * quat_array[2] + quat_array[0] * quat_array[1])
        t_4 = +1.0 - 2.0 * (quat_array[1] * quat_array[1] + quat_array[2] * quat_array[2])
        roll = math.atan2(t_3, t_4)

        return yaw, pitch, roll

    # Methods for envrionment interaction
    def step(self, action):
        self.do_simulation(action, self.frame_skip)
        # Extract the angle value
        quat_servo_mount = self.data.get_body_xquat("ServoHornMount_LEG1")[:4].copy()
        _, pitch_rad, _ = self.quat_to_euler(quat_servo_mount)
        target = self._get_current_target()
        accuracy_reward = abs(target) - abs(pitch_rad)
        rewards = -abs(accuracy_reward)
        if(pitch_rad > -0.5):
            rewards -= 10000

        observation = self._get_obs()
        info = {'Model Leg Pos (radians)': pitch_rad,
                'Target Leg Pos (radians)': target,
                'Time step': self.dt,
                'Reward yielded': rewards
                }
        self._idx += 1
        done = self._idx > (np.shape(self._target_leg_pos)[0] - 1)

        return observation, rewards, done, info   

    def _get_obs(self):
        return np.concatenate([
            self.sim.data.qpos.flat[2:].copy(),
            self.sim.data.qvel.flat.copy()
        ])

    def reset_model(self):
        qpos = self.init_qpos + self.np_random.uniform(low=-.1, high=.1, size=self.model.nq)
        qvel = self.init_qvel + self.np_random.randn(self.model.nv) * .1
        self.set_state(qpos, qvel)
        self._idx = 0
        return self._get_obs()

    def viewer_setup(self):
        self.viewer.cam.distance = 5

## LowCostPlatform
#  @brief  Creates a simple 3D model which is compatible with the Gym toolkit
class LowCostPlatform(mujoco_env.MujocoEnv, utils.EzPickle):
    ## Constructor
    #  @param xml_file The mujoco XML file created by the end user. 
    #  @param is_healthy Ensure servo motor is within limits (does not go over and break the leg)
    #  @param healthy_reward Prevent robot from farming rewards and not complete the task
    #  @param done Return true only if conditions are met (undecided as of now)
    def __init__(self, 
                healthy_reward=1.0,
                terminate_when_unhealthy=True,
                error_range=(0.05, 0.1)
                ):
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'SimpleLeg.xml')
        utils.EzPickle.__init__(self)

        # Local define variables and other data
        self._target_leg_pos = [0, 1, 2]
        self._idx = 0
        self._healthy_reward = healthy_reward
        self._terminate_when_unhealthy = terminate_when_unhealthy
        self._error_range = error_range

        mujoco_env.MujocoEnv.__init__(self, file_path, 5)

    ## Decorators for training
    @property
    def is_healthy(self):
        min_error, max_error = self._error_range
        is_healthy = min_error < self.accuracy < max_error
        return is_healthy

    @property 
    def done(self):
        done = (not self.is_healthy
                if self._terminate_when_unhealthy
                else False)
        return done

    # Methods for calcualtions on model joint angle 
    def add_trajectory(self, list_of_angles):
        self._target_leg_pos = list_of_angles

    def _get_current_target(self):
        return self._target_leg_pos[self._idx]

    def quat_to_euler(self, quat_array):
        t_0 = +2.0 * (quat_array[3] * quat_array[0] + quat_array[1] * quat_array[2])
        t_1 = +1.0 - 2.0 * (quat_array[0] * quat_array[0] + quat_array[1] * quat_array[1])
        yaw = math.atan2(t_0, t_1)

        t_2 = +2.0 * (quat_array[3] * quat_array[1] - quat_array[2] * quat_array[0])
        t_2 = +1.0 if t_2 > +1.0 else t_2
        t_2 = -1.0 if t_2 < -1.0 else t_2
        pitch = math.asin(t_2)

        t_3 = +2.0 * (quat_array[3] * quat_array[2] + quat_array[0] * quat_array[1])
        t_4 = +1.0 - 2.0 * (quat_array[1] * quat_array[1] + quat_array[2] * quat_array[2])
        roll = math.atan2(t_3, t_4)

        return yaw, pitch, roll

    # Methods for envrionment interaction
    def step(self, action):
        self.do_simulation(action, self.frame_skip)
        # Extract the angle value
        quat_servo_mount = self.data.get_body_xquat("ServoHornMount_LEG1")[:4].copy()
        _, pitch_rad, _ = self.quat_to_euler(quat_servo_mount)
        target = self._get_current_target()
        accuracy_reward = abs(target) - abs(pitch_rad)
        rewards = -accuracy_reward
        if(pitch_rad > -0.5):
            rewards -= 10000

        observation = self._get_obs()
        info = {'Model Leg Pos (radians)': pitch_rad,
                'Target Leg Pos (radians)': target,
                'Time step': self.dt,
                'Reward yielded': rewards
                }
        self._idx += 1
        done = self._idx > (np.shape(self._target_leg_pos)[0] - 1)

        return observation, rewards, done, info   

    def _get_obs(self):
        return np.concatenate([
            self.sim.data.qpos.flat[2:].copy(),
            self.sim.data.qvel.flat.copy()
        ])

    def reset_model(self):
        qpos = self.init_qpos + self.np_random.uniform(low=-.1, high=.1, size=self.model.nq)
        qvel = self.init_qvel + self.np_random.randn(self.model.nv) * .1
        self.set_state(qpos, qvel)
        self._idx = 0
        return self._get_obs()

    def viewer_setup(self):