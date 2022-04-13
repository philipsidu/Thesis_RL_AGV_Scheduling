import random
import pandas as pd


def generate_database(num_tasks):
    # list of all possible source nodes
    from_list = ["st1", "st2", "st3", "st4", "st5", "st6", "st7", "st8", "st9", "warehouse"]
    # list of all possible destination nodes
    to_list = ["st1", "st2", "st3", "st4", "st5", "st6", "st7", "st8", "st9"]

    # fill dataframe with random values for training
    conc_data = []
    for i in range(num_tasks):
        from_loc = random.sample(from_list, 1)
        to_loc = random.sample(to_list, 1)

        # check if from and to location is same
        while from_loc == to_loc:
            from_loc = random.sample(from_list, 1)

        # generate distance between from_location and to_location
        distance = generate_distance_for_tasks(from_loc[0], to_loc[0])
        velocity = 1
        time = distance

        # generate dictionary for each task and append it to the task list
        data = {'task_id': i + 1, 'from_locat': from_loc[0], 'to_locat': to_loc[0],
                'time': time, 'distance': distance}
        conc_data.append(data)

    # make pandas Dataframe from list
    df = pd.DataFrame(conc_data)
    return df


def sort_data(data, rule):
    if rule == 'fcfs':
        # first come, first served
        return data

    elif rule == 'std':
        # shortest travel distance
        new_data = sorted(data, key=lambda d: d['distance'])
        return new_data

    elif rule == 'edd':
        # earliest due date (tasks with remaining time are regarded as current tasks and executed first)
        new_data = sorted(data, key=lambda d: d['time'])
        return new_data

    elif rule == 'lwt':
        # longest waiting time
        new_data = sorted(data, key=lambda d: d['time'], reverse=True)
        return new_data

    elif rule == 'nvf':
        # nearest load point (get current positions of agv & assign agv to task with nearest from_locat)
        # first implement stations with time & distance & location of AGVs
        new_data = data

    else:
        raise NameError('None of the scheduling rules can be assigned to the current_data list!')


def generate_time_for_tasks(from_location, to_location):
    pass


def generate_distance_for_tasks(from_location, to_location):
    # distance in meters are returned depending on the from and to location
    if (from_location == 'warehouse') & (to_location == 'st1'):
        return random.randint(97, 103)

    elif (from_location == 'warehouse') & (to_location == 'st2'):
        return random.randint(48, 52)

    elif (from_location == 'warehouse') & (to_location == 'st3'):
        return random.randint(74, 76)

    elif (from_location == 'warehouse') & (to_location == 'st4'):
        return random.randint(122, 128)

    elif (from_location == 'warehouse') & (to_location == 'st5'):
        return random.randint(174, 176)

    elif (from_location == 'warehouse') & (to_location == 'st6'):
        return random.randint(198, 202)

    elif (from_location == 'warehouse') & (to_location == 'st7'):
        return random.randint(223, 227)

    elif (from_location == 'warehouse') & (to_location == 'st8'):
        return random.randint(248, 252)

    elif (from_location == 'warehouse') & (to_location == 'st9'):
        return random.randint(223, 227)

    elif ((from_location == 'st1') & (to_location == 'st2')) | ((from_location == 'st2') & (to_location == 'st1')):
        return random.randint(49, 51)

    elif ((from_location == 'st1') & (to_location == 'st3')) | ((from_location == 'st3') & (to_location == 'st1')):
        return random.randint(172, 178)

    elif ((from_location == 'st1') & (to_location == 'st4')) | ((from_location == 'st4') & (to_location == 'st1')):
        return random.randint(223, 225)

    elif ((from_location == 'st1') & (to_location == 'st5')) | ((from_location == 'st5') & (to_location == 'st1')):
        return random.randint(223, 225)

    elif ((from_location == 'st1') & (to_location == 'st6')) | ((from_location == 'st6') & (to_location == 'st1')):
        return random.randint(198, 202)

    elif ((from_location == 'st1') & (to_location == 'st7')) | ((from_location == 'st7') & (to_location == 'st1')):
        return random.randint(173, 178)

    elif ((from_location == 'st1') & (to_location == 'st8')) | ((from_location == 'st8') & (to_location == 'st1')):
        return random.randint(148, 152)

    elif ((from_location == 'st1') & (to_location == 'st9')) | ((from_location == 'st9') & (to_location == 'st1')):
        return random.randint(123, 127)

    elif ((from_location == 'st2') & (to_location == 'st3')) | ((from_location == 'st3') & (to_location == 'st2')):
        return random.randint(123, 127)

    elif ((from_location == 'st2') & (to_location == 'st4')) | ((from_location == 'st4') & (to_location == 'st2')):
        return random.randint(173, 178)

    elif ((from_location == 'st2') & (to_location == 'st5')) | ((from_location == 'st5') & (to_location == 'st2')):
        return random.randint(223, 227)

    elif ((from_location == 'st2') & (to_location == 'st6')) | ((from_location == 'st6') & (to_location == 'st2')):
        return random.randint(248, 252)

    elif ((from_location == 'st2') & (to_location == 'st7')) | ((from_location == 'st7') & (to_location == 'st2')):
        return random.randint(223, 227)

    elif ((from_location == 'st2') & (to_location == 'st8')) | ((from_location == 'st8') & (to_location == 'st2')):
        return random.randint(198, 202)

    elif ((from_location == 'st2') & (to_location == 'st9')) | ((from_location == 'st9') & (to_location == 'st2')):
        return random.randint(173, 177)

    elif ((from_location == 'st3') & (to_location == 'st4')) | ((from_location == 'st4') & (to_location == 'st3')):
        return random.randint(48, 52)

    elif ((from_location == 'st3') & (to_location == 'st5')) | ((from_location == 'st4') & (to_location == 'st5')):
        return random.randint(98, 102)

    elif ((from_location == 'st3') & (to_location == 'st6')) | ((from_location == 'st6') & (to_location == 'st3')):
        return random.randint(123, 127)

    elif ((from_location == 'st3') & (to_location == 'st7')) | ((from_location == 'st7') & (to_location == 'st3')):
        return random.randint(148, 152)

    elif ((from_location == 'st3') & (to_location == 'st8')) | ((from_location == 'st8') & (to_location == 'st3')):
        return random.randint(173, 178)

    elif ((from_location == 'st3') & (to_location == 'st9')) | ((from_location == 'st9') & (to_location == 'st3')):
        return random.randint(198, 202)

    elif ((from_location == 'st4') & (to_location == 'st5')) | ((from_location == 'st5') & (to_location == 'st4')):
        return random.randint(48, 52)

    elif ((from_location == 'st4') & (to_location == 'st6')) | ((from_location == 'st6') & (to_location == 'st4')):
        return random.randint(73, 77)

    elif ((from_location == 'st4') & (to_location == 'st7')) | ((from_location == 'st7') & (to_location == 'st4')):
        return random.randint(98, 102)

    elif ((from_location == 'st4') & (to_location == 'st8')) | ((from_location == 'st8') & (to_location == 'st4')):
        return random.randint(123, 127)

    elif ((from_location == 'st4') & (to_location == 'st9')) | ((from_location == 'st9') & (to_location == 'st4')):
        return random.randint(148, 152)

    elif ((from_location == 'st5') & (to_location == 'st6')) | ((from_location == 'st6') & (to_location == 'st5')):
        return random.randint(24, 26)

    elif ((from_location == 'st5') & (to_location == 'st7')) | ((from_location == 'st7') & (to_location == 'st5')):
        return random.randint(49, 51)

    elif ((from_location == 'st5') & (to_location == 'st8')) | ((from_location == 'st8') & (to_location == 'st5')):
        return random.randint(74, 76)

    elif ((from_location == 'st5') & (to_location == 'st9')) | ((from_location == 'st9') & (to_location == 'st5')):
        return random.randint(98, 102)

    elif ((from_location == 'st6') & (to_location == 'st7')) | ((from_location == 'st7') & (to_location == 'st6')):
        return random.randint(24, 26)

    elif ((from_location == 'st6') & (to_location == 'st8')) | ((from_location == 'st8') & (to_location == 'st6')):
        return random.randint(49, 51)

    elif ((from_location == 'st6') & (to_location == 'st9')) | ((from_location == 'st9') & (to_location == 'st6')):
        return random.randint(74, 76)

    elif ((from_location == 'st7') & (to_location == 'st8')) | ((from_location == 'st8') & (to_location == 'st7')):
        return random.randint(24, 26)

    elif ((from_location == 'st7') & (to_location == 'st9')) | ((from_location == 'st9') & (to_location == 'st7')):
        return random.randint(49, 51)

    elif ((from_location == 'st8') & (to_location == 'st9')) | ((from_location == 'st9') & (to_location == 'st8')):
        return random.randint(24, 26)
