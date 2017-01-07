import sys
import os
import pickle
import numpy as np
from numpy.matlib import repmat
import matplotlib.pyplot as plt
from scipy import stats

def get_fitness(over_data):
	data = over_data['data']
	gens = over_data['gens']
	fit_vec = [0]*gens

	for generation in data:
		gen_data = data[generation]
		fit_vec[int(generation)] = gen_data['fitness']

	best = data[gens-1]['pareto_front'][0]['genome']

	return fit_vec,best
if __name__ == "__main__":
	if len(sys.argv)<2:
		print 'FAIL'
		sys.exit()
	base_dir = 'Data/'
	directory_names = sys.argv[1:]


	stats_list = [ [], [],[],[] ]

	count = 0
	for directory in directory_names:
		file_list = os.listdir(directory+'.')
		for file_name in file_list:
			if len(file_name)>10:

				if file_name[-7:] == '.pickle':
					devo_layers = int(file_name.split('_')[1])
					print count, file_name
					count += 1
			
					curr_data = pickle.load(open(directory+file_name,'rb'))
					fit_list, best_robot = get_fitness(curr_data)
					stats_list[devo_layers-1].append(fit_list)
					# mat = best_robot.network.adj_matrix
					# nonzero = np.nonzero(mat[:,:,0])

					# for k in range(devo_layers):
					# 	print k,np.mean(mat[nonzero[0],nonzero[1],k])


	plt.figure()
	colors = ['b', 'r', 'g','y']
	legend = [0]*4
	for i in range(len(stats_list)):
		data = np.array(stats_list[i])
		avg = np.mean(data,axis=0)
		trial_max = np.max(data,axis=0)
		trial_min = np.min(data,axis=0)
		sem = stats.sem(data,axis=0)



		legend[i], = plt.plot(avg,colors[i],linewidth=2, label='$D_'+str(i+1)+'$')
		plt.fill_between(range(len(avg)),avg+2*sem,avg-2*sem, facecolor=colors[i], alpha=0.25)

	plt.xlabel('Generation',size=20)
	plt.ylabel('Fitness', size=20)
	plt.title('Fitness over Time', size=20)
	plt.legend(handles=legend,loc=2)
	plt.savefig('fitness.pdf')
	#plt.show()









