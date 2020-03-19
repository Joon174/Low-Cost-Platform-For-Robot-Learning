import gym

gym.envs.register(
	id = 'QUEEN-v1',
	entry_point = 'env.envRegister:QUEENv1',
	max_episode_steps = 1000,
	reward_threshold = 4800.0,
)

env = gym.make('QUEEN-v1')
env.reset()
while True:
	env.render()
	action = env.action_space.sample()
	env.step(action)
	print(action)
