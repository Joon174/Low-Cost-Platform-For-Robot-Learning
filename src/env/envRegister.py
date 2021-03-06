## @package envRegister.py
#  @brief This file contains the interface script for mujoco_py and the end user's model to be trained
#  @date 8-May-2020
#  @author Joon You Tan
#  @version 01.05.01

# Packages used for this file:
import math
import os
import numpy as np

# 
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

    def _get_next_target(self):
        if (self._idx + 1) <= len(self._target_leg_pos):
            state =  self._target_leg_pos[self._idx+1]
        else:
            state = self._target_leg_pos[self._idx]
        return state

    # Methods for envrionment interaction
    def step(self, action):
        self.do_simulation(action, self.frame_skip)
        pitch_rad = self.sim.data.qpos[5]
        # Extract the angle value
        target = self._get_current_target()
        self.accuracy = target - pitch_rad
        rewards = -self.accuracy**2

        observation = self._get_obs()
        info = {'Model Leg Pos (radians)': pitch_rad,
                'Target Leg Pos (radians)': target,
                'Time step': self.dt,
                'Reward yielded': rewards
                }
        self._idx += 1
        done = self._idx >= (np.shape(self._target_leg_pos)[0] - 1)
        # if (pitch_rad > 0.056 or pitch_rad < -0.79):
        #     rewards -= 100
        return observation, rewards, done, info   

    def _get_obs(self):
        return np.concatenate([
            self.sim.data.qpos.flat[5:].copy(),
            [self._get_next_target()],
            self.sim.data.qvel.flat[5:].copy()
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
                ctrl_cost_weight=0.5,
                 contact_cost_weight=5e-4,
                 healthy_reward=1.0,
                 terminate_when_unhealthy=True,
                 healthy_z_range=(1.0, 1.55),
                 contact_force_range=(-1.0, 1.0),
                 reset_noise_scale=0.1,
                 exclude_current_positions_from_observation=True):
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'PlatformV2.xml')
        utils.EzPickle.__init__(self)

        # Local define variables and other data
        self._ctrl_cost_weight = ctrl_cost_weight
        self._contact_cost_weight = contact_cost_weight

        self._healthy_reward = healthy_reward
        self._terminate_when_unhealthy = terminate_when_unhealthy
        self._healthy_z_range = healthy_z_range

        self._contact_force_range = contact_force_range

        self._reset_noise_scale = reset_noise_scale

        self._exclude_current_positions_from_observation = (
            exclude_current_positions_from_observation)

        self.xy_pos_before = 0
        self.xy_pos_after = 0
        self.total_time = 0

        mujoco_env.MujocoEnv.__init__(self, file_path, 5)

    @property
    def healthy_reward(self):
        return float(
            self.is_healthy
            or self._terminate_when_unhealthy
        ) * self._healthy_reward

    def control_cost(self, action):
        control_cost = self._ctrl_cost_weight * np.sum(np.square(action))
        return control_cost

    @property
    def contact_cost(self):
        contact_cost = self._contact_cost_weight * np.sum(
            np.square(self.contact_forces))
        return contact_cost

    @property
    def is_healthy(self):
        state = self.state_vector()
        min_z, max_z = self._healthy_z_range
        is_healthy = (np.isfinite(state).all() and min_z <= state[2] <= max_z)
        return is_healthy

    @property
    def contact_forces(self):
        raw_contact_forces = self.sim.data.cfrc_ext
        min_value, max_value = self._contact_force_range
        contact_forces = np.clip(raw_contact_forces, min_value, max_value)
        return contact_forces

    @property 
    def done(self):
        done = (not self.is_healthy
                if self._terminate_when_unhealthy
                else False)
        return done

    # Methods for envrionment interaction
    def step(self, action):
        self.xy_pos_before = self.get_body_com("Chasis")[:2].copy()
        self.do_simulation(action, self.frame_skip)
        self.xy_pos_after = self.get_body_com("Chasis")[:2].copy()

        xy_velocity = (self.xy_pos_after - self.xy_pos_before) / self.dt
        x_velocity, y_velocity = xy_velocity
        
        self.total_time += self.dt

        reward = (x_velocity + self.healthy_reward) - (self.contact_cost + self.control_cost(action))   
        done = self.done or (self.total_time > 30)
        observation = self._get_obs()
        info = {'Rewards': reward,
                'X_velocity': x_velocity,
                'Y_velocity': y_velocity
                }
        
        # Seconds
        if self.total_time > 120:
            self.total_time = 0

        return observation, reward, done, info

    def _get_obs(self):
        return np.concatenate([
            [self.sim.data.qpos.flat[0]],
            [self.sim.data.qpos.flat[6]],
            [self.sim.data.qpos.flat[12]],
            [self.sim.data.qpos.flat[18]],
            [self.sim.data.qvel.flat[0]],
            [self.sim.data.qvel.flat[6]],
            [self.sim.data.qvel.flat[12]],
            [self.sim.data.qvel.flat[18]]
        ])

    def reset_model(self):
        qpos = self.init_qpos + self.np_random.uniform(low=-.1, high=.1, size=self.model.nq)
        qvel = self.init_qvel + self.np_random.randn(self.model.nv) * .1
        self.set_state(qpos, qvel)
        return self._get_obs()

    def viewer_setup(self):
        self.viewer.cam.distance = 5