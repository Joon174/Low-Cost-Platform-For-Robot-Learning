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
#  @brief  Creates a simple 3D model which is compatible with the Gym toolkit
class ProofOfConceptModel(mujoco_env.MujocoEnv, utils.EzPickle):
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
    def healthy_reward(self):
        return float(
            self.is_healthy
            or self._terminate_when_unhealthy
        ) * self._healthy_reward

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
        t0 = +2.0 * (quat_array[3] * quat_array[0] + quat_array[1] * quat_array[2])
        t1 = +1.0 - 2.0 * (quat_array[0] * quat_array[0] + quat_array[1] * quat_array[1])
        yaw = math.atan2(t0, t1)

        t2 = +2.0 * (quat_array[3] * quat_array[1] - quat_array[2] * quat_array[0])
        t2 = +1.0 if t2 > +1.0 else t2
        t2 = -1.0 if t2 < -1.0 else t2
        pitch = math.asin(t2)

        t3 = +2.0 * (quat_array[3] * quat_array[2] + quat_array[0] * quat_array[1])
        t4 = +1.0 - 2.0 * (quat_array[1] * quat_array[1] + quat_array[2] * quat_array[2])
        roll = math.atan2(t3, t4)

        return yaw, pitch, roll

    # Methods for envrionment interaction
    def step(self, action):
        self.do_simulation(action, self.frame_skip)
        # Extract the angle value
        quat_servo_mount = self.data.get_body_xquat("ServoHornMount_LEG1")[:4].copy()
        _, pitch_rad, _ = self.quat_to_euler(quat_servo_mount)
        target = self._get_current_target()
        accuracy_reward = target - pitch_rad
        self.accuracy = -accuracy_reward
        rewards = self.accuracy + self.healthy_reward  

        observation = self._get_obs()
        info = {'Model Leg Pos (radians):': pitch_rad,
                'Target Leg Pos (radians)': target,
                'Reward yielded': rewards
                }
        done = False
        self._idx += 1

        if self._idx > (np.shape(self._target_leg_pos)[0] - 1):
            done = True

        return observation, rewards, done, info      

    def _get_obs(self):
        return np.concatenate([
            self.sim.data.qpos.flat[1:],
            self.sim.data.qvel.flat
        ])

    def reset_model(self):
        qpos = self.init_qpos + self.np_random.uniform(low=-.1, high=.1, size=self.model.nq)
        qvel = self.init_qvel + self.np_random.randn(self.model.nv) * .1
        self.set_state(qpos, qvel)
        self._idx = 0
        return self._get_obs()

    def viewer_setup(self):
        self.viewer.cam.distance = 5
