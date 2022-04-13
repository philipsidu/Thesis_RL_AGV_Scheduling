# from ... import ...
import numpy as np
import simpy
from tensorflow.keras.optimizers import Adam, SGD

from agent import Agent
from shop_floor import ShopFloor
# Press the green button in the gutter to run the script.


if __name__ == '__main__':
    model_config = {
        # ...
    }

# Initialize the parameter for the training process
target_update_size = 128  # number of timesteps after the main DQN updates the target network
batch_size = 20  # number of random samples from replay memory (maximum number of current task)
num_tasks = 300  # number of episodes for the training process (one training episode has 800 tasks)
timesteps_per_episode = 1000  # timesteps t for each episode
learning_rate = 0.7
discount_factor = 0.618

# Initialize the parameters for the environment
num_agv = 3
num_stations = 9

# Initialize the objects
env = simpy.Environment()

shopfloor = ShopFloor(env, num_tasks, num_agv)

env.process(shopfloor.task_arrival(env))
env.process(shopfloor.agv(env, 'AGV 1'))
env.process(shopfloor.agv(env, 'AGV 2'))
env.process(shopfloor.agv(env, 'AGV 3'))

env.run()

# optimizer = Adam(learning_rate=0.01)
# agent = Agent(env, optimizer)

# start training process
# agent.train_model(batch_size, timesteps_per_episode, num_episodes, learning_rate, target_update_size)
