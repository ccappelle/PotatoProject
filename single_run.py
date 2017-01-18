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

def run_experiment(generator_fcn,fitness_fcn,name,trial_num,pop_size,gens,eval_time,development_layers=1,envs = False):
	time_stamp = dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
	data = {}
	evolver = evolvers.AFPO(max_population_size=pop_size,generator_fcn=generator_fcn,fitness_fcn=fitness_fcn,environments = envs,
					development_layers=development_layers,max_generations=gens,eval_time=eval_time)
	data['pop_size'] = evolver.max_population_size
	data['gens'] = evolver.max_generations
	data['development_layers'] = evolver.development_layers
	data['eval_time'] = evolver.eval_time
	data['data'] = evolver.Evolve()
	data['motor_speed'] = robots.MOTOR_SPEED
	data['environments'] = envs
	data_folder = './Data'
	file_name = name+'_'+'_'+ str(trial_num) +'_'+ str(time_stamp) +'.pickle'

	if not os.path.isdir(data_folder):
		os.makedirs(data_folder)

	path_to_file = data_folder +'/'+file_name
	with open(path_to_file,'w') as f:
		pickle.dump(data,f)

	with open('last.txt','w') as f:
		f.write(path_to_file+'\n')
		
def run_quad(trial_num,pop_size,gens):
	generator_fcn = robots.Quadruped
	fitness_fcn = fit_func.Max_Y
	run_experiment(generator_fcn,fitness_fcn,'Quad',trial_num,pop_size,gens)

def run_treebot(tree_type,trial_num,envs,pop_size,gens,eval_time):	
	if tree_type == 'M' or tree_type == 'Modular':
		generator_fcn = robots.Treebot.Modular
	elif tree_type == 'NM' or tree_type == 'Nonmodular':
		generator_fcn = robots.Treebot.Non_Modular

	fitness_fcn = fit_func.Treebot

	run_experiment(generator_fcn,fitness_fcn,name=tree_type,trial_num=trial_num,
					pop_size=pop_size,gens=gens,eval_time=eval_time,envs=envs)


if __name__=="__main__":
	import sys
	trial_num = sys.argv[1]
	env_list = []
	distance = [4, 6]
	length = [1,2]
	LR = [1,2]
	num_LR = 2
	for lf in range(num_LR):
	 	for r in range(num_LR):
	 				env_list.append(environments.Cluster_Env.Bi_Sym(LR[lf],LR[r],distance[0],length[0]))
	# 		env_list.append(environments.Cluster_Env.Bi_Sym(left,right,distance,length))
	# #env = [env_list[0],env_list[1]]
	env = env_list

	run_treebot(tree_type='NM',trial_num=trial_num,envs=env,pop_size=100,gens=500,eval_time=100)





