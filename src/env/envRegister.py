import os
import numpy as np
from gym import utils
from gym.envs.mujoco import mujoco_env

class QUEENv1(mujoco_env.MujocoEnv, utils.EzPickle):
    def __init__(self, ctrl_cost_weight=0.5, contact_cost_weight=5e-4):
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'QUEEN_v1.xml')
		# Absolute path to your .xml MuJoCo scene file.
        mujoco_env.MujocoEnv.__init__(self, file_path, 5)
        utils.EzPickle.__init__(self)

        self._ctrl_cost_weight = ctrl_cost_weight
        self._contact_cost_weight = contact_cost_weight

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
