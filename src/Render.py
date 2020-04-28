## @package render.py
#  @brief Used to test if the algorithm can render the environment well.

import gym
from gym.envs.registration import register

# Register the environments for agent
# gym.envs.register(id='Queen-v1', entry_point='env.envRegister:QueenV1', max_episode_steps=1000, reward_threshold=4800.0)
register(
	id='ProofOfConceptModel-v0', 
	entry_point='env.envRegister:ProofOfConceptModel', 
	max_episode_steps=1000, 
	reward_threshold=4800.0,
	)

# Main Function
if __name__ == '__main__':
	# env = gym.make('Queen-v1')
	env = gym.make('ProofOfConceptModel-v0')
	env.reset()
	
	while True:
		env.render()
		action = env.action_space.sample()
		env.step(action)
