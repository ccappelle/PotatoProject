import robots
from pyrosim import PYROSIM
import evolvers
import numpy as np
import matplotlib.pyplot as plt
import pylab as P
NUM_IN_PARALLEL = 10

def Send_Entire_Population_To_Simulator(population):
	return Send_Sub_Population_To_Simulator(population,start_index=0)

def Send_Sub_Population_To_Simulator(population,start_index):
	sensor_data = {}
	ID = 0
	for offset in range(start_index,len(population),NUM_IN_PARALLEL):

		sims = [0]*NUM_IN_PARALLEL
		for i in range(NUM_IN_PARALLEL):
			if i+offset<len(population):
				sims[i] = PYROSIM(playBlind=True, evalTime = 1000)
				indv_to_send = population[i+offset]['genome']
				indv_to_send.Send_To_Simulator(sims[i],eval_time=1000)
				sims[i].Start()
		
		for i in range(NUM_IN_PARALLEL):
			if i+offset<len(population):
				sims[i].Wait_To_Finish()
				ID = population[i+offset]['ID']
				sensor_data[i+offset] = sims[i].Get_Results()

	return sensor_data

N1 = 1
N2 = 1000
N = N1*N2

data_vec = np.zeros((4,N))
mutant_vec = np.zeros((4,N))
diff_vec = np.zeros((4,N))
for dev in range(1,5):

	for i in range(N1):
		population = []

		for j in range(N2):
			indv = {}
			indv['genome'] = robots.Quadruped(development_layers=dev)
			indv['ID'] = j
			population.append(indv)
			print dev,i,j

		temp_data = Send_Entire_Population_To_Simulator(population)
		for j in range(N2):
			indv = {}
			indv['genome'] = population[j]['genome'].Copy_And_Mutate()
			indv['ID'] = j
			population[j] = indv

		mutant_data = Send_Entire_Population_To_Simulator(population)
		for index in temp_data:
			fit = evolvers.Max_Y(temp_data[index])
			mut_fit = evolvers.Max_Y(mutant_data[index])
			
			data_vec[dev-1, index+i*N2] = fit
			mutant_vec[dev-1, index+i*N2] = mut_fit
			diff = mut_fit - fit
			diff_vec[dev-1,index+i*N2] = diff
			print fit, mut_fit, diff, index+i*N2

vecs = [data_vec, mutant_vec, diff_vec]
titles = ['Random', 'Mutated', 'Difference']
colors = ['b', 'r', 'g','y']
for j in range(3):
	vec = vecs[j]
	title = titles[j]
	P.figure()
	P.title(title,size=20)
	P.xlabel('Fitness', size=20)
	P.xlim([-1.5, 1.5])

	for i in range(4):	
		n, bins, patches = P.hist(vec[i,:], 20,normed=1,histtype='step',color= colors[i],label='$D_'+str(i+1)+'$')
	P.legend()
	P.savefig(str(j)+".pdf")
#P.show()

