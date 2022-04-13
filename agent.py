import random
import progressbar

import numpy as np
import pandas as pd
import tensorflow as tf
from collections import deque
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input, Dense
from tensorflow.keras import backend as be

from shop_floor import ShopFloor as env


class Agent:
    def __init__(self, env, optimizer):
        self._state_size = env.observation_space
        self._action_size = env.action_space
        self._optimizer = optimizer

        # initialize the replay memory
        self.experience_memory = deque(maxlen=2000)

        # parameter for calculating the Q value in the target network
        self.gamma = 0.6
        # probability for selecting a random action
        self.epsilon = 0.1

        # initializing main and target dqn and align the model parameter
        self.dqn = self.build_compile_model()
        self.target_dqn = self.build_compile_model()
        self.align_target_params()

    def store_in_memory(self, state, action, reward, next_state, terminated):
        self.experience_memory.append((state, action, reward, next_state, terminated))

    def build_compile_model(self):
        model = Sequential()
        model.add(Input(shape=(self._state_size,)))
        model.add(Dense(8, activation=tf.nn.tanh))
        model.add(Dense(8, activation=tf.nn.tanh))
        model.add(Dense(15, activation='softmax'))

        model.compile(loss='mse', optimizer=self._optimizer)
        return model

    def align_target_params(self):
        self.target_dqn.set_weights(self.dqn.get_weights())

    def generate_action(self, state):
        # with probability epsilon select a random action
        if np.random.rand() <= self.epsilon:
            return env.sample_action()
        # otherwise, select action argmax(Q(s,a,theta))
        q_val = self.dqn.predict(state)
        return np.argmax(q_val[0])

    @staticmethod
    def calculate_loss_function(main_q_value, target_q_value):
        return (target_q_value - main_q_value)**2

    @staticmethod
    def update_dqn_gradient_descent(theta, learning_rate, loss_function):
        diff_part = learning_rate * be.gradients(loss_function, theta)
        theta_new = theta - diff_part
        return theta_new

    def retrain_model(self, batch_size, learning_rate):
        minibatch = random.sample(self.experience_memory, batch_size)

        for state, action, reward, next_state, terminated in minibatch:
            # predict value of the action value in main DQN
            dqn_pred = self.dqn.predict(state)

            # calculate the Q-value for the target network
            if terminated:
                target_dqn_pred = reward
            else:
                # s is no terminal state: make prediction with current target network
                target_pred = self.target_dqn.predict(next_state)
                # calculate the prediction value of the action value in the target DQN
                target_dqn_pred = reward + self.gamma * np.amax(target_pred)

            # calculate loss function
            loss = self.calculate_loss_function(dqn_pred, target_dqn_pred)

            # update the parameters of main DQN with gradient descent of the loss function
            theta = self.dqn.get_weights()
            theta_update = self.update_dqn_gradient_descent(theta, learning_rate, loss)
            self.dqn.set_weights(theta_update)

    def train_model_one_episode(self, batch_size, timesteps_per_episode, state, bar, learning_rate, target_update_size):
        for timestep in range(timesteps_per_episode):
            action = self.generate_action(state)

            # execute action and then observe the reward and next state
            next_state, reward, terminated = env.step(action)

            # store record in replay memory
            self.store_in_memory(state, action, reward, next_state, terminated)

            # update next state to current step
            state = next_state

            # as soon as replay memory contains more samples than the batch size: start training the main DQN model
            if len(self.experience_memory) > batch_size:
                self.retrain_model(batch_size, learning_rate)

            # update the target DQN model with the weights from the main DQN model
            if (timestep % target_update_size) == 0:
                self.align_target_params()

            if (timestep % 10) == 0:
                bar.update(timestep/10 + 1)

    @staticmethod
    def generate_database(num_episodes):
        # read in csv file
        df = pd.read_excel("train_task_data.xlsx", sheet_name="episode_task")
        # make dataframe empty
        if len(df.index) > 0:
            df = df.iloc[0:0]
        # list of all possible source nodes
        from_list = ["st1", "st2", "st3", "st4", "st5", "st6", "st7", "st8", "st9", "warehouse"]
        # list of all possible destination nodes
        to_list = ["st1", "st2", "st3", "st4", "st5", "st6", "st7", "st8", "st9"]

        # fill dataframe with random values for training
        conc_data = []
        for i in range(num_episodes):
            random.seed(42)
            from_loc = random.sample(from_list, 1)
            to_loc = random.sample(to_list, 1)
            # check if from and to location is same
            while from_loc == to_loc:
                from_loc = random.sample(from_list, 1)

            data = {'task_id': i + 1, 'from_locat': from_loc[0], 'to_locat': to_loc[0],
                    'time': random.normalvariate(0.5, 0.1)}
            conc_data.append(data)

        # make pandas Dataframe
        df = pd.DataFrame(conc_data)
        # store dataframe in excel file
        df.to_excel("train_task_data.xlsx", sheet_name="episode_task", index=False)

    def train_model(self, batch_size, timesteps_per_episode, num_episodes, learning_rate, target_update_size):
        for e in range(num_episodes):
            # obtain the current state
            state = env.reset()
            # generate database for training (saved in csv file: train_task.csv)
            self.generate_database(num_episodes)

            # initialize the total reward (each episode new reward?)
            total_reward = 0

            bar = progressbar.ProgressBar(maxval=timesteps_per_episode / 10,
                                          widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
            bar.start()
            self.train_model_one_episode(batch_size, timesteps_per_episode, state, bar, learning_rate, target_update_size)
            bar.finish()

            # still dunno what that means (render environment after every 10 episodes)
            if (e + 1) % 10 == 0:
                print('******************************')
                print('Episode: {}'.format(e + 1))
                env.render()
                print('******************************')
