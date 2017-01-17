#!/usr/bin/env python
import numpy as np
import environments
def Treebot(data, environment):
	
	distance, color, time_steps,num_sensors = Parse_Treebot_Data(data)
	fitness = 0

	percent_of_eval_time = .5
	eval_start = int(time_steps * (1.-percent_of_eval_time))
	#eval_start = 0
	eval_end = time_steps
	num_to_eval = eval_end - eval_start

	for sensor in range(2):
		for time in range(eval_start,eval_end):
			color_vec = color[sensor,time,:]
			if np.array_equal(color_vec,environments.Cluster_Env.ODD_COLOR):
				fitness -= 1
			elif np.array_equal(color_vec,environments.Cluster_Env.EVEN_COLOR):
				fitness += 1

	odd, even = environment.Get_Odd_And_Even()
	lo = odd * num_to_eval * -1
	hi = even * num_to_eval * 1
	normalized_fitness = float(fitness-lo)/float(hi-lo)

	return normalized_fitness

def Parse_Treebot_Data(data):
	num_sensors = 0
	time_steps = 0

	for entry in data:
		sensor = entry[0]
		sensor_offset = entry[1]
		time = entry[2]

		num_sensors = max(num_sensors,sensor)
		time_steps = max(time_steps,time)

	num_sensors = num_sensors+1
	time_steps = time_steps +1

	distance = np.zeros((num_sensors,time_steps))
	color = np.zeros((num_sensors,time_steps,3))

	for entry in data:
		sensor = entry[0]
		sensor_offset = entry[1]
		time = entry[2]

		if sensor_offset ==0:
			distance[sensor,time] = data[entry]
		else:
			color[sensor,time,sensor_offset-1] = data[entry]

	return distance,color,time_steps,num_sensors

def Max_XY(sensor_data):
	POS_SENSOR = 4
	Y_DIR = 1
	return sensor_data[POS_SENSOR,1,EVAL_TIME-1]+sensor_data[POS_SENSOR,0,EVAL_TIME-1]
def Max_Y(sensor_data):
	POS_SENSOR = 4
	Y_DIR = 1
	return sensor_data[POS_SENSOR,1,EVAL_TIME-1]