import robots
import evolvers
from evolvers import AFPO
import os
import sys
import time
import pickle
import datetime as dt


def run_quad(trial_num,pop_size,gens,development_layers):
	generator_fcn = robots.Quadruped
	fitness_fcn = evolvers.Max_Y
	time_stamp = dt.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
	data = {}
	evolver = evolvers.AFPO(pop_size,generator_fcn,fitness_fcn,development_layers=development_layers,max_generations=gens)
	data['pop_size'] = evolver.max_population_size
	data['gens'] = evolver.max_generations
	data['development_layers'] = evolver.development_layers
	data['eval_time'] = evolver.eval_time
	data['data'] = evolver.Evolve()
	data['motor_speed'] = robots.MOTOR_SPEED
	data_folder = './Data/'
	file_name = 'Quad_'+str(development_layers)+'_'+ str(trial_num) +'_'+ str(time_stamp) +'.pickle'

	if not os.path.isdir(data_folder):
		os.makedirs(data_folder)

	path_to_file = data_folder +'/'+file_name
	with open(path_to_file,'w') as f:
		pickle.dump(data,f)

if __name__=='__main__':
	gens = 1000
	development_layers = 2

	trial_num = 0
	pop_size = 50
	args = sys.argv

	if len(args)>=2:
		trial_num = int(args[1])
	if len(args)>=3:
		development_layers = int(args[2])
	if len(args)>=4:
		gens = int(args[3])

	if len(args)>=5:
		pop_size = int(args[4])

	run_quad(trial_num,pop_size,gens,development_layers)