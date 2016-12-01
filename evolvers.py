from pyrosim import PYROSIM
from operator import itemgetter
import random
import numpy as np
import copy

EVAL_TIME = 1000
MAX_GENERATIONS = 300
NUM_IN_PARALLEL = 10
class Evolver(object):
	def __init__(self,max_population_size,generator_fcn,fitness_fcn={},max_generations=MAX_GENERATIONS,eval_time=EVAL_TIME,maximize=True,
					development_layers = 1):
		
		self.population = []
		self.max_population_size = max_population_size
		self.generator_fcn = generator_fcn
		self.fitness_fcn = fitness_fcn
		self.eval_time = eval_time
		self.nextID = 0
		self.maximize = maximize
		self.generation = 0
		self.max_generations = max_generations
		self.development_layers = development_layers

		for i in range(self.max_population_size):
			self.Add_Random_Individual()


	def Add_Individual(self,genome):
		indv = {}
		indv['genome'] = genome
		indv['ID'] = self.nextID
		indv['fitness'] = 0
		indv['evaluated'] = False
		self.nextID += 1
		self.population.append(indv)
		

	def Add_Random_Individual(self):
		indv = {}
		color = [random.random(),random.random(),random.random()]
		indv['genome'] = self.generator_fcn(development_layers=self.development_layers,color=color)
		indv['fitness'] = 0
		indv['evaluated'] = False
		indv['ID'] = self.nextID
		self.nextID += 1
		self.population.append(indv)
 
 	def Send_Population_To_Simulator(self):
 		start_index_found = False
 		start_index = 0
 		i = 0
 		while not start_index_found:
 			if self.population[i]['evaluated'] == False:
 				start_index = i
 				start_index_found = True
 			i += 1
 		return self.Send_Sub_Population_To_Simulator(start_index)

 	def Send_Entire_Population_To_Simulator(self):
 		return self.Send_Sub_Population_To_Simulator(start_index=0)

	def Send_Sub_Population_To_Simulator(self,start_index):
		sensor_data = {}
		ID = 0
		for offset in range(start_index,len(self.population),NUM_IN_PARALLEL):

			sims = [0]*NUM_IN_PARALLEL
			for i in range(NUM_IN_PARALLEL):
				if i+offset<len(self.population):
					sims[i] = PYROSIM(playBlind=True, evalTime = self.eval_time)
					indv_to_send = self.population[i+offset]['genome']
					indv_to_send.Send_To_Simulator(sims[i],eval_time=self.eval_time)
					sims[i].Start()
			
			for i in range(NUM_IN_PARALLEL):
				if i+offset<len(self.population):
					sims[i].Wait_To_Finish()
					ID = self.population[i+offset]['ID']
					sensor_data[i+offset] = sims[i].Get_Results()

		return sensor_data

	def Sort_Population(self):
		self.population.sort(key=itemgetter('fitness') ,reverse=self.maximize)

	def Evaluate_Population(self):
		sensor_data = self.Send_Population_To_Simulator()
		#sensor_data = self.Send_Entire_Population_To_Simulator()
		for index in sensor_data:
			
			self.population[index]['fitness'] = self.fitness_fcn(sensor_data[index])
			self.population[index]['evaluated'] = True
		
	def Mutate_And_Copy_Genome(self,index):
		mutant_genome = self.population[index]['genome'].Copy_And_Mutate()
		return mutant_genome

	def Remove_Individual(self,index):
		del sel.population[index]


class AFPO(Evolver):
	def __init__(self,*args,**kwargs):
		super(AFPO,self).__init__(*args,**kwargs)


	def Add_Random_Individual(self):
		super(AFPO,self).Add_Random_Individual()
		indv = self.population[-1]
		indv['age'] = 0
		indv['num_dominated_by'] = 0
		indv['is_dominated'] = False

	def Add_Individual(self,genome,age):
		super(AFPO,self).Add_Individual(genome)
		self.population[-1]['age'] = age
		self.population[-1]['num_dominated_by'] = 0
		self.population[-1]['is_dominated'] = False


	def Age_Population(self):
		for g in self.population:
			g['age'] += 1

	def Cull_All_Dominated(self):
		pop_length = len(self.population)
		for i in range(pop_length-1,-1,-1):
			if self.population[i]['is_dominated']:
				del self.population[i]

	def Cull_To_Pop_Size(self):
		#Assumes population is sorted by fitness and num-dominated appropiately
		index = len(self.population)-1
		while len(self.population)> self.max_population_size:
			del(self.population[index])
			index -= 1

		
	def Count_Dominated_By(self):
		for i in range(len(self.population)):
			indv_1 = self.population[i]
			for j in range(i+1,len(self.population)):	
				indv_2 = self.population[j]

				which_dominates = self.Which_Dominates(indv_1,indv_2)
				if which_dominates == 1:
					indv_2['num_dominated_by'] += 1
					indv_2['is_dominated'] = True
				elif which_dominates == 2:
					indv_1['num_dominated_by'] += 1
					indv_1['is_dominated'] = True

	def Which_Dominates(self,indv_1,indv_2):
		if self.maximize:
			indv_1_is_fitter = indv_1['fitness'] > indv_2['fitness']
		else:
			indv_1_is_fitter = indv_1['fitness'] < indv_2['fitness']

		if indv_1['age']< indv_2['age']:
			if indv_1_is_fitter or indv_1['fitness'] == indv_2['fitness']:
				return 1
			else:
				return 0
		elif indv_1['age'] > indv_2['age']:
			if not(indv_1_is_fitter) or indv_1['fitness'] == indv_2['fitness']:
				return 2
			else:
				return 0
		elif indv_1['age'] == indv_2['age']:
			if indv_1_is_fitter:
				return 1
			elif indv_1['fitness'] == indv_2['fitness']:
				if indv_1['ID'] < indv_2['ID']:
					return 2
				else:
					return 1
			elif not(indv_1_is_fitter):
				return 2
		else:
			return 0


	def Evolve(self):
		best = {}
		for i in range(self.max_generations):
			fitness,pareto_front = self.Evolve_For_One_Generation()
			best[i] = {}
			best[i]['fitness'] = fitness
			if i%100 == 0 or i == self.max_generations-1:
				best[i]['pareto_front'] = pareto_front
		return best

	def Evolve_For_One_Generation(self):

		self.Evaluate_Population()

		self.Count_Dominated_By()

		self.Sort_Population()


		self.Cull_To_Pop_Size()

		pareto_front_size = self.Get_Pareto_Front()
		fit_list = [0]*pareto_front_size
		id_list = [0]*pareto_front_size

		for i in range(len(fit_list)):
			fit_list[i] = self.population[i]['fitness']
			id_list[i] = self.population[i]['ID']

		pareto_front = self.population[0:pareto_front_size]
		print self.generation, fit_list, pareto_front_size, self.population[0]['age']

		self.Age_Population()

		#self.Fill_Population()
		self.Fill_Population_To_Double()

		self.Add_Random_Individual()

		self.Make_All_Non_Dominated()
 		
		self.generation += 1

		return fit_list[0],pareto_front

	def Get_Pareto_Front(self):
		index = 0

		for index in range(len(self.population)):
			if self.population[index]['is_dominated'] == True:
				return index

		return len(self.population)-1

	def Fill_Population(self):
		num_survivors = len(self.population)
		for i in range(num_survivors,self.max_population_size-1):
			r = random.randint(0,num_survivors-1)
			mutant = self.population[r]['genome'].Copy_And_Mutate()
			#mutant = self.Mutate_And_Copy_Genome(r)
			age = self.population[r]['age']
			self.Add_Individual(mutant, age)

	def Fill_Population_To_Double(self):
		for i in range(len(self.population)):
			mutant = self.Mutate_And_Copy_Genome(i)
			age = self.population[i]['age']
			self.Add_Individual(mutant,age)


	def Make_All_Non_Dominated(self):
		for p in self.population:
			p['is_dominated'] = False
			p['num_dominated_by'] = 0

	def Sort_Population(self):		
		super(AFPO,self).Sort_Population()
		self.population.sort(key=itemgetter('num_dominated_by'))
		
		id_list = [0]*len(self.population)
		for i in range(len(self.population)):
			id_list[i] =  self.population[i]['ID']



def Max_XY(sensor_data):
	POS_SENSOR = 4
	Y_DIR = 1
	return sensor_data[POS_SENSOR,1,EVAL_TIME-1]+sensor_data[POS_SENSOR,0,EVAL_TIME-1]
def Max_Y(sensor_data):
	POS_SENSOR = 4
	Y_DIR = 1
	return sensor_data[POS_SENSOR,1,EVAL_TIME-1]

def Play_Indv(dumped_data, index=-1):
	gens = dumped_data['gens']
	gen_data = dumped_data['data']
	eval_time = dumped_data['eval_time']
	print eval_time
	if index==-1:
		index = gens-1

	fitness = gen_data[index]['fitness']
	pareto_front = gen_data[index]['pareto_front']
	best = pareto_front[0]['genome']
	print fitness
	sim = PYROSIM(playPaused=False,playBlind=False,evalTime=eval_time)
	best.Send_To_Simulator(sim,eval_time=eval_time)
	sim.Start()

def _Test_Dev_Layers():
	from robots import Quadruped
	evolver = AFPO(50, Quadruped,Max_Y,development_layers=2, max_generations=10)
	evolver.Evolve()


if __name__ == "__main__":
	pass
	import pickle
	# with open('Data/Quad_4_2016-11-17_14:28:29.pickle') as f:
	# 	data = pickle.load(f)

	# Play_Indv(data)
	_Test_Dev_Layers()
	#Sample_Run()

