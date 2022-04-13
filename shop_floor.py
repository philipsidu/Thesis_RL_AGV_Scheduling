import simpy
import random

import pandas as pd

from utils import sort_data, generate_distance_for_tasks, generate_database


class ShopFloor(object):
    def __init__(self, env, num_tasks, num_agv):
        self.env = env
        self.num_tasks = num_tasks
        self.num_task_done = 0
        self.num_current_tasks = 0

        # create 3 AGVs, 9 Stations & 18 Storages (Warehouse and Carport missing)
        self.agv_task = simpy.Resource(env, capacity=num_agv)
        self.agv_task_req = None
        # self.station = simpy.Resource(env, capacity=num_stations)
        # self.storage = simpy.Resource(env, capacity=num_storages)

        # create task DataFrames (distance and time?)
        self.all_data = generate_database(self.num_tasks)
        self.current_data = []

        # generate a dictionary with rules and assign values from 1 to 5 to the rules
        self.rule_dict = {1: 'fcfs', 2: 'std', 3: 'edd', 4: 'lwt', 5: 'nvf'}
        # specify scheduling rule for whole process (if no RL is used)
        self.num_rule = 1
        # get rule from the dictionary above
        self.scheduling_rule = self.rule_dict[self.num_rule]

        # create resource for maximum 20 current tasks
        self.current_tasks = simpy.Store(env, capacity=20)
        # create variable for requesting one slot of the resource
        self.store_task_req = None
        self.task_req = None

        # create events
        self.task_arrives = env.event()
        self.task_scheduled = env.event()
        # self.task_executed = self.env.event()

        print('init done')

    def task_arrival(self, env):
        while len(self.all_data) > 0:
            start = env.now

            # task arrival rate N(45s, 15s)
            print(f'task arrival process starts: {start:.3f} seconds after simulation start.')
            print('-------------------------------------------------------------')

            task_arrival_time = random.normalvariate(45, 15)
            # prevent an error occurring when task_arrival_time is negative (very rare)
            while task_arrival_time < 0:
                task_arrival_time = random.normalvariate(45, 15)

            yield env.timeout(task_arrival_time)

            end = env.now

            # print time for task arrival
            arrival_time = end - start
            print(f'task arrived after: {arrival_time:.3f} seconds in current tasks.')

            # freeze as long as num_current_tasks is 20
            yield self.current_tasks.put(self.all_data.iloc[0, :].to_dict())

            # print(f'List of Items in Store: {self.current_tasks.items}')
            print(f'{len(self.current_tasks.items)} of {self.current_tasks.capacity} slots are allocated '
                  f'in current tasks.')

            # sort current_data list with given rule
            self.current_tasks.items = sort_data(self.current_tasks.items, self.scheduling_rule)

            # update num_current_tasks
            self.num_current_tasks = len(self.current_tasks.items)
            # print('current_data contains of', self.num_current_tasks, 'tasks')

            self.task_arrives.succeed()
            self.task_arrives = env.event()

            # check if all_data not empty
            if len(self.all_data) > 1:
                # pop task which is processed to current_data
                self.all_data = self.all_data.iloc[1:, :]
            else:
                # if final task has been processed to current_task --> empty all_data
                self.all_data = self.all_data.iloc[0:0]
                print('All tasks have been processed to current_tasks')
            print('-------------------------------------------------------------')

    @staticmethod
    def get_time_from_current_data(task: dict) -> int:
        return task.get('time')

    def schedule_task(self, env, num_task_done, num_agv_req, agv_name):
        # problem: all three AGVs are requested as soon as one task arrives (number request <= number tasks)
        if self.num_current_tasks > 0:
            # while num_agv_req <= self.num_current_tasks: # not sure if it works (dunno if multiple agvs come here)
            # generate request for scheduling task to agv
            self.agv_task_req = self.agv_task.request()
            print(self.agv_task_req)

            # update number of used AGVs
            num_agv_req = self.agv_task.count
            # print status information about agv usage
            print(f'{self.agv_task.count} of {self.agv_task.capacity} AGVs are in usage right now.')

            # freeze task scheduling as long as all three AGVs are in usage
            yield self.agv_task_req

            start_task = env.now

            # get time from current_data's first task
            time = self.get_time_from_current_data()

            print('task', self.current_data[0].get('task_id'), 'is executed by', agv_name,
                  'Expected time:', time, 'seconds')
            print('-------------------------------------------------------------')

            yield env.timeout(time)

            print('task', self.current_data[0].get('task_id'), 'is done')

            num_task_done += 1
            end_task = env.now

            print('task', self.current_data[0].get('task_id'), 'was executed in',
                  end_task - start_task, 'seconds', 'by', agv_name)

            # update current_data & num_current_tasks
            self.current_data = self.current_data[1:]
            print('number of done tasks:', num_task_done)
            self.num_current_tasks = len(self.current_data)

            # release the first resource slot
            req = self.max_current_tasks.users[0]
            yield self.max_current_tasks.release(req)
            print('-------------------------------------------------------------------------')

        if self.num_current_tasks == 0 & len(self.all_data) == 0:
            print('All tasks have been executed. Simulation is terminated!')
            print('-------------------------------------------------------------------------')

    def agv(self, env, agv_name):
        yield self.task_arrives

        while self.num_task_done != self.num_tasks:
            if len(self.current_tasks.items) > 0:
                print('task scheduling process for', agv_name, 'begins')

                # get task information and release a slot in the Store current_tasks
                task = self.current_tasks.items[0]
                yield self.current_tasks.get()

                # freeze task scheduling as long as all three AGVs are in usage
                yield self.agv_task.request()

                print(f'{agv_name} successfully requested a task for execution. '
                      f'Task slot {self.agv_task.count} will be executed')

                # print(f'before get: {self.current_tasks.items}')
                # task = self.current_tasks.items[0]
                # yield self.current_tasks.get()
                # print(f'after get: {self.current_tasks.items}')

                # get time from current_data's first task
                time = self.get_time_from_current_data(task)
                task_id = task.get('task_id')
                print(f'task {task_id} is executed by {agv_name}. Expected time: {time:.2f} seconds')

                # print status information about agv usage
                # print(f'{num_agv_req} of {self.agv_task.capacity} AGVs are in usage right now.')

                print('-------------------------------------------------------------')

                start_task = env.now

                yield env.timeout(time)

                end_task = env.now

                self.num_task_done += 1

                time_task = end_task - start_task
                print(f'task {task_id} was executed in {time_task:.2f} seconds by {agv_name}')

                print(f'number of done tasks: {self.num_task_done}')
                self.num_current_tasks = len(self.current_tasks.items)

                # release the agv slot
                req_agv = self.agv_task.users[0]
                yield self.agv_task.release(req_agv)
                print('-------------------------------------------------------------------------')

            else:
                yield self.task_arrives

            # if len(self.current_tasks.items) == 0 & len(self.all_data) == 0:
            #     print('All tasks have been executed. Simulation is terminated!')
            #     print('-------------------------------------------------------------------------')

    # def reset(self):
    #     state = self.observation_space
    #     return state

    # def step(self):
    #     pass

    # def sample_action(self):
    # with probability epsilon generate action? Dunno what meant, maybe remove later
    #     pass
