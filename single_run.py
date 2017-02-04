import evolvers
from evolvers import AFPO
import os
import sys
import time
import pickle
import datetime as dt
import robots
import fitness_functions as fit_func
import environments
import json
from pyrosim import PYROSIM

def run_experiment(generator_fcn,fitness_fcn,name,trial_num,pop_size,gens,eval_time,
					env_order, dimensions,env_space = False, fitness_threshold=False,development_layers=1,
					):
	time_stamp = dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	data = {}

	envs_to_train_in = [env_space[i] for i in env_order]

	evolver = evolvers.AFPO(max_population_size=pop_size,generator_fcn=generator_fcn,fitness_fcn=fitness_fcn,
					environments = envs_to_train_in,
					development_layers=development_layers,
					max_generations=gens,eval_time=eval_time,
					fitness_threshold=fitness_threshold)


	data['pop_size'] = evolver.max_population_size
	#data['fitness_function'] = fitness_function
	data['development_layers'] = evolver.development_layers
	data['eval_time'] = evolver.eval_time


	evolved_data = evolver.Evolve()
	gens = evolver.generation-1
	data['gens'] = gens
	best_robot = evolved_data[gens]['pareto_front'][0]['genome']
	data['data'] = evolved_data
	data['best_robot'] = best_robot
	data['motor_speed'] = robots.MOTOR_SPEED
	data['environments'] = envs_to_train_in
	data['env_space'] = env_space
	data['name'] = name
	data['threshold'] = fitness_threshold
	data['dimensions'] = dimensions
	data['num_trained_in'] = len(envs_to_train_in)


	env_fitness = [0]*16
	for index,env in enumerate(env_space):
		sim = PYROSIM(playBlind=True,playPaused=False,evalTime=eval_time)
		ids = best_robot.Send_To_Simulator(sim,eval_time=eval_time)
		env.Send_To_Simulator(sim, ID_offset=ids[0])

		sim.Start()
		sim.Wait_To_Finish()
		sensor_data = sim.Get_Results()
		 
		env_fitness[index] = fitness_fcn(sensor_data,env)


	data_folder = './Data'
	file_name = name+'_'+ str(trial_num) +'_'+str(len(env_order))+'_'+str(dimensions)+'_'+ str(time_stamp)
	print file_name
	pickle_file_name = file_name +'.pickle'
	json_file_name = file_name+'.json'
	if not os.path.isdir(data_folder):
		os.makedirs(data_folder)

	pickle_path_to_file = data_folder +'/'+pickle_file_name
	json_path_to_file = data_folder + '/' + json_file_name

	with open(pickle_path_to_file,'w') as f:
		pickle.dump(data,f)



	#Create json daat
	json_data = {}
	
	print 'env fit', env_fitness
	print 'env order', env_order
	#store json data
	json_data['env_fitness'] = env_fitness
	json_data['type'] = name
	json_data['threshold'] = fitness_threshold
	json_data['dimensions'] = dimensions
	json_data['num_trained_in'] = len(envs_to_train_in)
	json_data['env_order'] = env_order

	#Write json
	with open(json_path_to_file,'w') as f:
		json.dump(json_data,f)



def run_cont_experiment(*args,**kwargs):
	count = 0
	while count <= 30:
		run_experiment(*args,**kwargs)
		count += 1

def run_quad(trial_num,pop_size,gens):
	generator_fcn = robots.Quadruped
	fitness_fcn = fit_func.Max_Y
	run_experiment(generator_fcn,fitness_fcn,'Quad',trial_num,pop_size,gens)

def run_treebot(tree_type,trial_num,env_order,env_space,pop_size,gens,eval_time,fitness_threshold,constant,dimensions,color_on):	
	print 'Waaaat ',color_on
	if tree_type == 'M' or tree_type == 'Modular':
		if color_on:
			generator_fcn = robots.Treebot.MC
			tree_type = tree_type + 'C'
		else:
			generator_fcn = robots.Treebot.Modular
	elif tree_type == 'NM' or tree_type == 'Nonmodular':
		if color_on:
			generator_fcn = robots.Treebot.NMC
			tree_type = tree_type +'C'
		else:
			generator_fcn = robots.Treebot.Non_Modular
	print tree_type
	fitness_fcn = fit_func.Treebot
	if constant:
		run_cont_experiment(generator_fcn,fitness_fcn,name=tree_type,trial_num=trial_num,
						pop_size=pop_size,gens=gens,eval_time=eval_time,
						env_order=env_order,env_space=env_space,
						fitness_threshold=fitness_threshold,dimensions=dim_num)
	else:
		run_experiment(generator_fcn,fitness_fcn,name=tree_type,trial_num=trial_num,
						pop_size=pop_size,gens=gens,eval_time=eval_time,
						env_order=env_order,env_space=env_space,
						fitness_threshold=fitness_threshold,dimensions=dim_num)



if __name__=="__main__":
	import sys
	import numpy as np
	trial_num = sys.argv[1]
	tree_type = str(sys.argv[2])
	dim_num = int(sys.argv[3])

	THRESHOLD = .9
	distance_vals = [4,6]
	length_vals = [1,2]
	num_in = [1,2]
	num_LR = 2
	env_list = [0]*16

	order = [0,3]
	if dim_num == 3:
		#order = [0,3,4,7]
		order =[3,4]
	elif dim_num == 4:
		order = [0,3,4,7,8,11,12,15]

	env_space=[]
	env_tuple_list = []
	for length in length_vals:
		for distance in distance_vals:
			for left in num_in:
				for right in num_in:
					env_tuple = (length,distance,left,right)
					env_tuple_list.append(env_tuple)
					env_object = environments.Cluster_Env.Bi_Sym(left,right,distance,length)
					env_space.append(env_object)
	

	#run_treebot(tree_type=tree_type,trial_num=trial_num,
	#			env_order=order,env_space=env_space,
	#			pop_size=50,gens=100000,eval_time=100,
	#			fitness_threshold=THRESHOLD,constant=True, dimensions=dim_num,color_on=False)

	run_treebot(tree_type=tree_type,trial_num=trial_num,
				env_order=order,env_space=env_space,
				pop_size=50,gens=100000,eval_time=100,
				fitness_threshold=THRESHOLD,constant=True, dimensions=dim_num,color_on=True)



