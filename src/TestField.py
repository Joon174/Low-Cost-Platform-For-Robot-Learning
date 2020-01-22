import gym

gym.envs.register(
	id = 'Prototype-v1',
	entry_point = 'envs.prototype1_v1:Prototype1EnvV1',
	max_episode_steps = 1000,
	reward_threshold = 500.0,
)

env = gym.make('Prototype-v1')
env.reset()
env.render()
input("Wow very cool.")