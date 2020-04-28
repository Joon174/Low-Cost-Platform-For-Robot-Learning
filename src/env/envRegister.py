## @package envRegister.py
#  @brief Custom package used to register the custom made robot model to be acccessible by OpenAI gym's toolkit
#  @param xml_file: robot modelled in XML

import os
import numpy as np
from gym import utils
from gym.envs.mujoco import mujoco_env

"""
ProofOfConceptModel
@param: is_healthy: Ensure servo motor is within limits (does not go over and break the leg)
        healthy_reward: Prevent robot from farming rewards and not complete the task
        done: Return true only if conditions are met (undecided as of now)
"""
class ProofOfConceptModel(mujoco_env.MujocoEnv, utils.EzPickle):
    def __init__(self, healthy_reward=1.0):
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'SimpleLeg.xml')
        mujoco_env.MujocoEnv.__init__(self, file_path, 5)
        utils.EzPickle.__init__(self)
        # Variables to be used in the analysis
        self.current_leg_pos = 0
        self.target_leg_pos = 0
        self._healthy_reward = healthy_reward
    
    @property
    def is_healthy(self):
        return is_healthy

    @property
    def healthy_reward(self):
        return float(

        )

    @property 
    def done(self):
        done = False

        return done

    def add_trajectory(self, list_of_angles):
        self.target_leg_pos = list_of_angles

    def step(self, action):
        self.healthy_reward = 0
        self.do_simulation(action, self.frame_skip)
        xy_position = self.get_body_com("EndEffector_LEG1")[:2].copy()
        accuracy_reward = 0
        rewards = accuracy_reward + self.healthy_reward  

        observation = self._get_obs()
        info = {'Sample Dictionary': 0}
        done = False

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
        return self._get_obs()

    def viewer_setup(self):
        self.viewer.cam.distance = 5

"""
The class below has been commmented out until the power circuit has been developed properly.
class QueenV1(mujoco_env.MujocoEnv, utils.EzPickle):
    def __init__(self, ctrl_cost_weight=0.5, contact_cost_weight=5e-4):
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'QUEEN_v1.xml')
		# Absolute path to your .xml MuJoCo scene file.
        mujoco_env.MujocoEnv.__init__(self, file_path, 5)
        utils.EzPickle.__init__(self)

        self.__ctrl_cost_weight = ctrl_cost_weight
        self.__contact_cost_weight = contact_cost_weight

    def step(self, action):
		#Carry out one step of action
        xy_position_before = self.get_body_com("QUEEN_Chasis")[:2].copy()
        self.do_simulation(action, self.frame_skip)
        xy_position_after = self.get_body_com("QUEEN_Chasis")[:2].copy()

        xy_velocity = (xy_position_after - xy_position_before) / self.dt
        x_velocity, y_velocity = xy_velocity

        rewards = x_velocity	
        done = False
        observation = self._get_obs()
        info = {0 : 'SomeDummyData'}

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
        return self._get_obs()

    def viewer_setup(self):
        self.viewer.cam.distance = 5
"""