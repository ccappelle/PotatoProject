from pyrosim import PYROSIM
from operator import itemgetter
import random
import numpy as np
import copy
import pickle
import datetime as dt
import time

EVAL_TIME = 1000
MAX_GENERATIONS = 300
NUM_IN_PARALLEL = 10
def Env_Mean(fitness_vec):
	return sum(fitness_vec)/float(len(fitness_vec))

def Env_Weighted_Average(fitness_vec):
	weigted_avg = 0
	sorted_vec = sorted(fitness_vec)
	fitness = 0.
	for i in range(len(fitness_vec)):
		if not(i == len(fitness_vec)-1):
			modifier = 1./(2.**(i+1.)) #exponential decay on weighting term
		fitness += sorted_vec[i]*modifier

	return fitness


def Env_Worst(fitness_vec):
	return min(fitness_vec)

class Evolver(object):
	def __init__(self,max_population_size,generator_fcn,
					environments = False,
					fitness_fcn={},max_generations=MAX_GENERATIONS,
					eval_time=EVAL_TIME,maximize=True,
					development_layers = 1,
					env_avg_func=Env_Weighted_Average,
					fitness_threshold = False):
		
		self.population = []
		self.max_population_size = max_population_size
		self.generator_fcn = generator_fcn
		self.fitness_fcn = fitness_fcn
		self.env_avg_func = env_avg_func
		self.eval_time = eval_time
		self.nextID = 0
		self.maximize = maximize
		self.generation = 0
		self.max_generations = max_generations
		self.development_layers = development_layers
		self.fitness_threshold = fitness_threshold

		self.environments = []
		if not environments:
			environments = [environments.Environment()]
		for env in environments:
			self.environments.append(env)

		for i in range(self.max_population_size):
			self.Add_Random_Individual()


	def Add_Individual(self,genome):
		indv = {}
		indv['genome'] = genome
		indv['ID'] = self.Get_Next_ID()
		indv['env_fitness'] = [0]*len(self.environments)
		indv['fitness'] = 0
		indv['evaluated'] = False

		self.population.append(indv)
		

	def Add_Random_Individual(self):
		color = [random.random(),random.random(),random.random()]
		#genome = self.generator_fcn(development_layers=self.development_layers,color=color)
		genome = self.generator_fcn()
		indv = {}
		indv['genome'] = genome
		indv['ID'] = self.nextID
		indv['env_fitness'] = [0]*len(self.environments)
		indv['fitness'] = 0
		indv['evaluated'] = False
		self.population.append(indv)

 	def Get_Next_ID(self):
 		ID = self.nextID
 		self.nextID += 1
 		return ID

 	def Send_Population_To_Simulator(self,environment=0):
 		start_index_found = False
 		start_index = 0
 		i = 0
 		while not start_index_found:
 			if self.population[i]['evaluated'] == False:
 				start_index = i
 				start_index_found = True
 			i += 1
 		return self.Send_Sub_Population_To_Simulator(start_index,environment=environment)

 	def Send_Entire_Population_To_Simulator(self):
 		return self.Send_Sub_Population_To_Simulator(start_index=0,environment=environment)

	def Send_Sub_Population_To_Simulator(self,start_index,environment=0):
		sensor_data = {}
		ID = 0
		for offset in range(start_index,len(self.population),NUM_IN_PARALLEL):

			sims = [0]*NUM_IN_PARALLEL
			for i in range(NUM_IN_PARALLEL):
				if i+offset<len(self.population):
					sims[i] = PYROSIM(playBlind=True, evalTime = self.eval_time)
					indv_to_send = self.population[i+offset]['genome']
					offsets = indv_to_send.Send_To_Simulator(sims[i],eval_time=self.eval_time)
					self.environments[environment].Send_To_Simulator(sims[i],ID_offset=offsets[0])
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

		for i in range(len(self.environments)):
			sensor_data = self.Send_Population_To_Simulator(environment=i)			
			for index in sensor_data:
				if 'environment' in self.fitness_fcn.__code__.co_varnames:
					self.population[index]['env_fitness'][i] = self.fitness_fcn(sensor_data[index],environment=self.environments[i])
				else:
					self.population[index]['env_fitness'][i] = self.fitness_fcn(sensor_data[index])
		for index in range(len(self.population)):
			# choose which function to specify total fitness
			#self.population[index]['fitness'] = Env_Weighted_Average(self.population[index]['env_fitness'])
			#self.population[index]['fitness'] = Env_Worst(self.population[index]['env_fitness'])
			self.population[index]['fitness'] = self.env_avg_func(self.population[index]['env_fitness'])
			self.population[index]['evaluated'] = True

		#sensor_data = self.Send_Entire_Population_To_Simulator()
				
	def Mutate_And_Copy_Genome(self,index):
		mutant_genome = self.population[index]['genome'].Copy_And_Mutate()
		return mutant_genome

	def Remove_Individual(self,index):
		del sel.population[index]

	def Quick_Save(self):
		time_stamp = dt.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
		file_path = './Data/'+time_stamp+'.pickle'

		data = self.population[0]

		with open(file_path,'w') as f:
			pickle.dump(data,f)

class AFPO(Evolver):
	def __init__(self,*args,**kwargs):
		super(AFPO,self).__init__(*args,**kwargs)
		self.start_time = dt.datetime.now().strftime('%H:%M:%S')

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
			if self.fitness_threshold:
				end_flag = True
				for env_fitness in pareto_front[0]['env_fitness']:
					if env_fitness< self.fitness_threshold:
						end_flag = False
				if end_flag:
					best[i]['pareto_front'] = pareto_front	
					return best
			if i%100 == 0 or i == self.max_generations-1:
				best[i]['pareto_front'] = pareto_front
			#if i%50 == 0 and i>0:
			#	self.Quick_Save()
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
		print self.generation
		print '	Best Fitness', fit_list[0]
		print '	Environment fit', self.population[0]['env_fitness']
		print '	Age', self.population[0]['age']
		print ' Time', self.start_time, dt.datetime.now().strftime('%H:%M:%S')
		print '\n'

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






def _Test_Dev_Layers():
	from robots import Quadruped
	evolver = AFPO(50, Quadruped,Max_Y,development_layers=2, max_generations=10)
	evolver.Evolve()


if __name__ == "__main__":
	pass
	

