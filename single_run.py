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

def run_experiment(generator_fcn,fitness_fcn,name,trial_num,pop_size,gens,eval_time,development_layers=1,envs = False, fitness_threshold=False):
	time_stamp = dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	data = {}
	evolver = evolvers.AFPO(max_population_size=pop_size,generator_fcn=generator_fcn,fitness_fcn=fitness_fcn,environments = envs,
					development_layers=development_layers,max_generations=gens,eval_time=eval_time, fitness_threshold=fitness_threshold)
	data['pop_size'] = evolver.max_population_size
	data['gens'] = evolver.max_generations
	data['development_layers'] = evolver.development_layers
	data['eval_time'] = evolver.eval_time
	data['data'] = evolver.Evolve()
	data['motor_speed'] = robots.MOTOR_SPEED
	data['environments'] = envs
	data_folder = './Data'
	file_name = name+'_'+ str(trial_num) +'_'+str(len(envs))+'_'+ str(time_stamp) +'.pickle'

	if not os.path.isdir(data_folder):
		os.makedirs(data_folder)

	path_to_file = data_folder +'/'+file_name
	with open(path_to_file,'w') as f:
		pickle.dump(data,f)

	with open('last.txt','w') as f:
		f.write(path_to_file+'\n')

def run_cont_experiment(*args,**kwargs):
	while True:
		run_experiment(*args,**kwargs)

def run_quad(trial_num,pop_size,gens):
	generator_fcn = robots.Quadruped
	fitness_fcn = fit_func.Max_Y
	run_experiment(generator_fcn,fitness_fcn,'Quad',trial_num,pop_size,gens)

def run_treebot(tree_type,trial_num,envs,pop_size,gens,eval_time,fitness_threshold,constant):	
	if tree_type == 'M' or tree_type == 'Modular':
		generator_fcn = robots.Treebot.Modular
	elif tree_type == 'NM' or tree_type == 'Nonmodular':
		generator_fcn = robots.Treebot.Non_Modular

	fitness_fcn = fit_func.Treebot
	if constant:
		run_cont_experiment(generator_fcn,fitness_fcn,name=tree_type,trial_num=trial_num,
						pop_size=pop_size,gens=gens,eval_time=eval_time,envs=envs,
						fitness_threshold=fitness_threshold)
	else:
		run_experiment(generator_fcn,fitness_fcn,name=tree_type,trial_num=trial_num,
						pop_size=pop_size,gens=gens,eval_time=eval_time,envs=envs,
						fitness_threshold=fitness_threshold)



if __name__=="__main__":
	import sys
	import numpy as np
	trial_num = sys.argv[1]
	tree_type = str(sys.argv[2])
	dim_num = int(sys.argv[3])


	env_dict = {} 
	distance_vals = [4,6]
	length_vals = [1,2]
	num_in = [1,2]
	num_LR = 2
	for i,left in enumerate(num_in):
	 	for j,right in enumerate(num_in):
	 		for k,distance in enumerate(distance_vals):
	 			for l,length in enumerate(length_vals):
	 				env = environments.Cluster_Env.Bi_Sym(left,right,distance,length)
	 				env_dict[i,j,k,l]=env
	

	env_list = []
	count = 0

	for key in env_dict:
		i = key[0]
		j = key[1]
		k = key[2]
		l = key[3]
		count += 1
		if dim_num >= 2:
			if i==j and k == 0 and l == 0:
				env_list.append(env_dict[key])
		if dim_num >= 3:
			if i==j and k == 1 and l == 0:
				env_list.append(env_dict[key])
		if dim_num >= 4:
			if i==j  and l == 1:
				env_list.append(env_dict[key])


	run_treebot(tree_type=tree_type,trial_num=trial_num,envs=env_list,pop_size=50,gens=5000,eval_time=100,fitness_threshold=.9,constant=True)





