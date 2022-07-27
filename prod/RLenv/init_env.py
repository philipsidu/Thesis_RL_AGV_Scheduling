import random
import progressbar
import statistics
import numpy as np
import pandas as pd
import datetime as dt


from collections import deque, defaultdict

from prod.RLenv.source import *
from prod.RLenv.production_env import *


PRINT_CONSOLE = False
EPSILON = 0.000001
EXPORT_FREQUENCY = 10 ** 3
EXPORT_NO_LOGS = False

PATH_TIME = "log/" + dt.datetime.now().strftime("%Y%m%d_%H%M%S")


def define_production_parameters(env, episode):
    """
    Determine the production system parameters here
    :param env: production environment (simpy)
    :param episode: the number of the current episode
    :return parameters: dictionary containing all necessary parameters
    """
    parameters = dict()
    parameters.update(({'SEED': 10}))
    random.seed(parameters['SEED'] + episode)

    parameters.update({'NUM_ORDERS': 10 ** 8})  # Default: large number to not run out of orders

    parameters.update({'time_end': 0.0})

    parameters.update({'stop_criteria': env.event()})
    parameters.update({'step_criteria': env.event()})
    parameters.update({'continue_criteria': env.event()})

    parameters.update(({'EXPONENTIAL_SMOOTHING': 0.01}))  # Default: 0.01
    parameters.update(({'EPSILON': EPSILON}))
    parameters.update(({'PRINT_CONSOLE': PRINT_CONSOLE}))
    parameters.update(({'EXPORT_NO_LOGS': EXPORT_NO_LOGS}))

    parameters.update(({'PATH_TIME': PATH_TIME}))
    parameters.update(({'EXPORT_FREQUENCY': EXPORT_FREQUENCY}))

    parameters.update(({'CHANGE_SCENARIO_AFTER_EPISODES': 5 * 10 ** 10}))

    extend_agent_parameters(parameters=parameters)
    extend_production_parameters(parameters=parameters)

    # Export parameter config to csv
    pd.DataFrame.from_dict(parameters, orient="index").to_csv(parameters['PATH_TIME'] + "_config_parameters.txt",
                                                              sep=",")

    return parameters


def extend_agent_parameters(parameters):
    """
    The parameters dictionary is extended with agent parametes
    :param parameters: parameters dictionary
    """
    # In this setting the RL-agent (TRPO-Algorithm) is controlling the transport decision making
    # Alternatives: TRPO, FIFO, NJF, EMPTY
    parameters.update({'TRANSP_AGENT_TYPE': "TRPO"})
    # Alternatives: bin_buffer_fill, bin_machine_failure, bin_location, int_buffer_fill, rel_buffer_fill,
    # rel_buffer_fill_in_out, order_waiting_time, order_waiting_time_normalized, distance_to_action,
    # remaining_process_time, total_process_time
    parameters.update({'TRANSP_AGENT_STATE': ['rel_buffer_fill_in_out', 'bin_machine_failure']})
    # Alternatives: valid_action, utilization, waiting_time_normalized, throughput, conwip, const_weighted,
    # weighted_objectives
    parameters.update({'TRANSP_AGENT_REWARD': "utilization"})
    # Alternatives: valid_action, utilization, waiting_time
    parameters.update({'TRANSP_AGENT_REWARD_SPARSE': ""})
    # Episode limit counter, default = 0
    parameters.update({'TRANSP_AGENT_REWARD_EPISODE_LIMIT': 0})
    # Alternatives: valid, entry, exit, time
    parameters.update({'TRANSP_AGENT_REWARD_EPISODE_LIMIT_TYPE': "valid"})
    # Standard: [1.0, 1.0]  |  First: Const weight values for action to machine, Second: weight for action to sink
    parameters.update({'TRANSP_AGENT_REWARD_SUBSET_WEIGHTS': [1.0, 1.0]})
    # tbf
    parameters.update({'TRANSP_AGENT_REWARD_OBJECTIVE_WEIGHTS': {'utilization': 1.0, 'waiting_time': 1.0}})
    # tbf
    parameters.update({'TRANSP_AGENT_REWARD_WAITING_ACTION': 0.0})
    # tbf
    parameters.update({'TRANSP_AGENT_REWARD_INVALID_ACTION': 0.0})
    # Number of invalid actions until forced action is choosen
    parameters.update({'TRANSP_AGENT_MAX_INVALID_ACTIONS': 5})
    # Waiting time of waiting time action
    parameters.update({'TRANSP_AGENT_WAITING_TIME_ACTION': 2})
    # Alternatives: direct, resource
    parameters.update({'TRANSP_AGENT_ACTION_MAPPING': 'direct'})
    # Alternatives: True, False
    parameters.update({'TRANSP_AGENT_WAITING_ACTION': False})
    # Alternatives: True, False
    parameters.update({'TRANSP_AGENT_EMPTY_ACTION': False})
    # ConWIP inventory target if conwip reward is selected
    parameters.update({'TRANSP_AGENT_CONWIP_INV': 15})
    # Forced order transport if threshold reached
    parameters.update({'WAITING_TIME_THRESHOLD': 1000})


def extend_production_parameters(parameters):
    """

    :param parameters:
    :return:
    """
    # Number of transportation resources
    parameters.update({'NUM_TRANSP_AGENTS': 1})
    # Number of machines in the environment
    parameters.update({'NUM_MACHINES': 8})
    # Number of sources in the environment
    parameters.update({'NUM_SOURCES': 3})
    # Number of sinks in the environment
    parameters.update({'NUM_SINKS': 3})
    # Total number of resourses in the environment
    parameters.update({'NUM_RESOURCES': parameters['NUM_MACHINES'] + parameters['NUM_SOURCES']
                                        + parameters['NUM_SINKS']})

    parameters.update({'NUM_PROD_VARIANTS': 1})
    parameters.update({'NUM_PROD_STEPS': 1})

    # Transport parameters
    parameters.update({'TRANSP_SPEED': 1.0 * 60.0})
    # check code in .ipynb
    parameters.update({'RESP_AREA_TRANSP': [[[True for i in range(parameters['NUM_RESOURCES'])]
                                             for j in range(parameters['NUM_RESOURCES'])]
                                            for k in range(parameters['NUM_TRANSP_AGENTS'])]})

    # Source parameters
    # Number of load ports
    parameters.update({'SOURCE_CAPACITIES': [3] * parameters['NUM_SOURCES']})
    # Orders for which machines are created in the specific source
    parameters.update({'RESP_AREA_SOURCE': [[0, 1], [2, 3, 4], [5, 6, 7]]})
    # Mean Time Order Generation
    parameters.update({'MTOG': [10.0, 10.0, 10.0]})
    # Alternatives: ALWAYS_FILL_UP, MEAN_ARRIVAL_TIME
    parameters.update({'SOURCE_ORDER_GENERATION_TYPE': "ALWAYS_FILL_UP"})

    # Machine parameters
    # Alternatives: FIFO -> Decision rule for selecting the next available order from the load port
    parameters.update({'MACHINE_AGENT_TYPE': "FIFO"})
    parameters.update({'MACHINE_GROUPS': [2, 1, 1, 1, 1, 3, 3, 3]})

    parameters.update({'MIN_PROCESS_TIME': [0.5] * parameters['NUM_MACHINES']})
    parameters.update({'AVERAGE_PROCESS_TIME': [60.0] * parameters['NUM_MACHINES']})
    parameters.update({'MAX_PROCESS_TIME': [150.0] * parameters['NUM_MACHINES']})
    # Default: Not used
    parameters.update({'CHANGEOVER_TIME': 0.0})
    # Unscheduled breakdowns
    parameters.update({'MTBF': [1000.0] * parameters['NUM_MACHINES']})
    parameters.update({'MTOL': [200.0] * parameters['NUM_MACHINES']})
    # Capacity for in and out machine buffers together
    parameters.update({'MACHINE_CAPACITIES': [6] * parameters['NUM_MACHINES']})

    # Order parameters
    # Probability which machine allocated, when orders are created
    parameters.update({'ORDER_DISTRIBUTION': [1.0 / parameters['NUM_MACHINES']] * parameters['NUM_MACHINES']})
    # Probability which product variant, when orders are created
    parameters.update({'VARIANT_DISTRIBUTION': [1.0 / parameters['NUM_PROD_VARIANTS']] * parameters['NUM_PROD_VARIANTS']})

    # Handling time
    parameters.update({'TIME_TO_LOAD_MACHINE': 60.0 / 60.0})
    parameters.update({'TIME_TO_UNLOAD_MACHINE': 60.0 / 60.0})
    parameters.update({'TIME_TO_LOAD_SOURCE': 60.0 / 60.0})
    parameters.update({'TIME_TO_UNLOAD_SOURCE': 60.0 / 60.0})

    # Transport time
    parameters.update({'TRANSP_DISTANCE': [[50.0 for x in range(parameters['NUM_RESOURCES'])]
                                           for y in range(parameters['NUM_RESOURCES'])]})
    parameters.update({'TRANSP_TIME': [[0.0 for x in range(parameters['NUM_RESOURCES'])]
                                       for y in range(parameters['NUM_RESOURCES'])]})
    for i in range(parameters['NUM_RESOURCES']):
        for j in range(parameters['NUM_RESOURCES']):
            parameters['TRANSP_TIME'][i][j] = parameters['TRANSP_DISTANCE'][i][j] / parameters['TRANSP_SPEED']
            if i == j:
                parameters['TRANSP_TIME'][i][j] = 0.0
    parameters.update({'MAX_TRANSP_TIME': np.array(parameters['TRANSP_TIME']).max()})

    return parameters


def define_production_statistics(parameters):
    """
    Statistic arrays for performance evaluation
    :param parameters: parameters dictionary
    :return:
    """
    statistics = dict()
    stat_episode = dict()

    statistics.update({'stat_machines_working': np.array([0.0] * parameters['NUM_MACHINES'])})
    statistics.update({'stat_machines_broken': np.array([0.0] * parameters['NUM_MACHINES'])})
    statistics.update({'stat_machines_idle': np.array([0.0] * parameters['NUM_MACHINES'])})
    statistics.update({'stat_machines_changeover': np.array([0.0] * parameters['NUM_MACHINES'])})
    statistics.update({'stat_machines_processed_orders': np.array([0.0] * parameters['NUM_MACHINES'])})
    statistics.update({'stat_machines': [statistics['stat_machines_working'], statistics['stat_machines_broken'],
                                         statistics['stat_machines_idle'], statistics['stat_machines_changeover']]})

    statistics.update({'stat_transp_working': np.array([0.0] * parameters['NUM_TRANSP_AGENTS'])})
    statistics.update({'stat_transp_walking': np.array([0.0] * parameters['NUM_TRANSP_AGENTS'])})
    statistics.update({'stat_transp_handling': np.array([0.0] * parameters['NUM_TRANSP_AGENTS'])})
    statistics.update({'stat_transp_idle': np.array([0.0] * parameters['NUM_TRANSP_AGENTS'])})
    statistics.update({'stat_transp': [statistics['stat_transp_walking'], statistics['stat_transp_idle']]})
    statistics.update({'stat_transp_selected_idle': np.array([0] * parameters['NUM_TRANSP_AGENTS'])})
    statistics.update({'stat_transp_forced_idle': np.array([0] * parameters['NUM_TRANSP_AGENTS'])})
    statistics.update({'stat_transp_threshold_waiting_reached': np.array([0] * parameters['NUM_TRANSP_AGENTS'])})

    statistics.update({'stat_order_sop': defaultdict(int)})
    statistics.update({'stat_order_eop': defaultdict(int)})
    statistics.update({'stat_order_waiting': defaultdict(int)})
    statistics.update({'stat_order_processing': defaultdict(int)})
    statistics.update({'stat_order_handling': defaultdict(int)})
    statistics.update({'stat_order_leadtime': defaultdict(int)})

    statistics.update(
        {'stat_order': [statistics['stat_order_sop'], statistics['stat_order_eop'], statistics['stat_order_waiting'],
                        statistics['stat_order_processing'], statistics['stat_order_handling'],
                        statistics['stat_order_leadtime']]})

    statistics.update({'stat_inv_buffer_in': np.array([0.0] * parameters['NUM_RESOURCES'])})
    statistics.update({'stat_inv_buffer_out': np.array([0.0] * parameters['NUM_RESOURCES'])})
    statistics.update({'stat_inv_buffer_in_mean': [np.array([0.0] * parameters['NUM_RESOURCES']),
                                                   np.array([0.0] * parameters['NUM_RESOURCES'])]})
    statistics.update({'stat_inv_buffer_out_mean': [np.array([0.0] * parameters['NUM_RESOURCES']),
                                                    np.array([0.0] * parameters['NUM_RESOURCES'])]})
    statistics.update({'stat_inv': [statistics['stat_inv_buffer_in'], statistics['stat_inv_buffer_out']]})
    statistics.update({'stat_inv_episode': [[0.0, 0]]})

    statistics.update({'stat_agent_reward': [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]})

    statistics.update({'agent_reward_log': open(parameters['PATH_TIME'] + "_agent_reward_log.txt", "w")})
    statistics.update({'episode_log': open(parameters['PATH_TIME'] + "_episode_log.txt", "w")})
    statistics.update({'episode_statistics': ['stat_machines_working', 'stat_machines_changeover',
                                              'stat_machines_broken', 'stat_machines_idle', 'stat_machines_processed_orders',
                                              'stat_transp_working', 'stat_transp_walking', 'stat_transp_handling',
                                              'stat_transp_idle']})

    statistics.update({'sim_start_time': ""})
    statistics.update({'sim_end_time': ""})

    statistics.update({'stat_prefilled_orders': ""})

    # Episode KPI Logger
    statistics.update({'episode_log_header': ['episode_counter','sim_step','sim_time','dt','dt_real_time','valid_actions','total_reward','machines_working','machines_changeover','machines_broken','machines_idle','processed_orders','transp_working','transp_walking','transp_handling','transp_idle','machines_total','selected_idle','forced_idle','threshold_waiting','finished_orders','order_waiting_time','alpha','inventory']})
    string = ""
    for x in statistics['episode_log_header']:
        string = string + x + ","
    string = string[:-1]
    statistics['episode_log'].write("%s\n" % (string))

    # Reward Agent Logger
    string = "episode,sim_step,sim_time,action,reward,action_valid,state"
    statistics['agent_reward_log'].write("%s\n" % (string))
    statistics['agent_reward_log'].close()

    # Temp statistics
    for stat in statistics['episode_statistics']:
        stat_episode.update({stat: np.array([0.0] * len(statistics[stat]))})

    statistics.update({'orders_done': deque()})

    return statistics, stat_episode


def define_production_resources(env, statistics, parameters, agents, time_calc):
    """
    Define resources which are used in the simpy environment
    :param env: simpy environment
    :param statistics:
    :param parameters:
    :param agents:
    :param time_calc:
    :return:
    """
    resources = dict()

    # Create an environment and start the setup process
    resources.update({'machines': [Machine(env=env, id=i, capacity=parameters['MACHINE_CAPACITIES'][i],
                     agent_type=parameters['MACHINE_AGENT_TYPE'],
                     machine_group=parameters['MACHINE_GROUPS'][i],
                     statistics=statistics, parameters=parameters, resources=resources, agents=agents, time_calc=time_calc,
                     location= None, label= None)
                        for i in range(parameters['NUM_MACHINES'])]})
    resources.update({'sources': [Source(env=env, id=i + parameters['NUM_MACHINES'], capacity=parameters['SOURCE_CAPACITIES'][i],
                     resp_area=parameters['RESP_AREA_SOURCE'][i],
                     statistics=statistics, parameters=parameters, resources=resources, agents=agents, time_calc=time_calc,
                     location=None, label=None)
                        for i in range(parameters['NUM_SOURCES'])]})
    resources.update({'sinks': [Sink(env=env, id=i + parameters['NUM_MACHINES'] + parameters['NUM_SOURCES'],
                     statistics=statistics, parameters=parameters, resources=resources, agents=agents, time_calc=time_calc,
                     location=None, label=None)
                        for i in range(parameters['NUM_SINKS'])]})

    temp_resources = []
    temp_resources.extend(resources['machines'])
    temp_resources.extend(resources['sources'])
    temp_resources.extend(resources['sinks'])

    resources.update({'all_resources': temp_resources})

    resources.update({'transps': [Transport(env=env, id=i, resp_area=parameters['RESP_AREA_TRANSP'][i],
                                                  agent_type=parameters['TRANSP_AGENT_TYPE'],
                                                  statistics=statistics, parameters=parameters, resources=resources,
                                                  agents=agents, time_calc=time_calc, location=None, label=None)
                                        for i in range(parameters['NUM_TRANSP_AGENTS'])]})

    resources.update({'repairman': simpy.PreemptiveResource(env, capacity=parameters['NUM_MACHINES'])})

    env.process(other_jobs(env, resources['repairman']))

    # Create source and machine normalizers
    source_wt_normalizer = ZScoreNormalization('exp', alpha=0.01)
    machine_wt_normalizer = ZScoreNormalization('exp', alpha=0.01)
    for mach in resources['machines']:
        mach.machine_wt_normalizer = machine_wt_normalizer
    for sourc in resources['sources']:
        sourc.source_wt_normalizer = source_wt_normalizer

    print("All resources types: ", [x.type for x in resources['all_resources']])
    print("All resources ids: ", [x.id for x in resources['all_resources']])
    print("Number of machines: ", len(resources['machines']))
    print("Number of sources: ", len(resources['sources']))
    print("Number of sinks: ", len(resources['sinks']))

    return resources
