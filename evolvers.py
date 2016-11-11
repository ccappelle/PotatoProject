from pyrosim import PYROSIM
from operator import itemgetter
import random
import numpy as np

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
					sensor_data[i+offset] = sims[i].Get_Results()

		return sensor_data

	def Sort_Population(self):
		self.population.sort(key=itemgetter('fitness') ,reverse=self.maximize)

	def Evaluate_Population(self):
		sensor_data = self.Send_Population_To_Simulator()
		for i in sensor_data:
			self.population[i]['fitness'] = self.fitness_fcn(sensor_data[i])
			self.population[i]['evaluated'] = True
		
	def Mutate_And_Copy_Genome(self,index):
		mutant = self.population[index]['genome'].Copy_And_Mutate()
		return mutant

	def Remove_Individual(self,index):
		del sel.population[index]


class AFPO(Evolver):
	def __init__(self,*args,**kwargs):
		super(AFPO,self).__init__(*args,**kwargs)


	def Add_Random_Individual(self):
		super(AFPO,self).Add_Random_Individual()
		self.population[-1]['age'] = 0
		self.population[-1]['num_dominated_by'] = 0
		self.population[-1]['is_dominated'] = False

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
		start_index = len(self.population)
		for i in range(start_index-1,self.max_population_size-1,-1):
			del self.population[i]
		
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
			best[i] = self.Evolve_For_One_Generation()

		return best

	def Evolve_For_One_Generation(self):

		self.Evaluate_Population()

		self.Count_Dominated_By()

		self.Sort_Population()


		self.Cull_To_Pop_Size()

		pareto_front = self.Get_Pareto_Front()

		print self.generation, self.population[0]['fitness'], self.population[0]['age'],pareto_front,len(self.population)

		self.Age_Population()

		#self.Fill_Population()
		self.Fill_Population_To_Double()

		self.Add_Random_Individual()

		self.Make_All_Non_Dominated()
 		
		self.generation += 1

		return self.population[0:pareto_front]

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
			#mutant = self.population[r]['genome'].Copy_And_Mutate()
			mutant = self.Mutate_And_Copy_Genome(r)
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
		


def Max_XY(sensor_data):
	POS_SENSOR = 4
	Y_DIR = 1
	return sensor_data[POS_SENSOR,1,EVAL_TIME-1]+sensor_data[POS_SENSOR,0,EVAL_TIME-1]
def Max_Y(sensor_data):
	POS_SENSOR = 4
	Y_DIR = 1
	return sensor_data[POS_SENSOR,1,EVAL_TIME-1]

def Show(best,N_SHOWS=3):
	indices = np.linspace(0,len(best)-1,num=N_SHOWS)

	for i in indices:
		i = int(i)
		robot_list = best[i]
		IDs = [0,0,0,0]
		sim = PYROSIM(playBlind=False,playPaused=False,evalTime=EVAL_TIME,xyz=(0.,-5.,4.),hpr=(90.0,-25.,0.0))
		N = len(robot_list)
		if N>5:
			N=5
		xVec = np.linspace(-N/2,N/2,num=N)
		for i in range(N):
			robot = robot_list[i]
			IDs = robot['genome'].Send_To_Simulator(sim,x_offset=xVec[i], objID=IDs[0],jointID=IDs[1],sensorID=IDs[2],neuronID=IDs[3])
		sim.Start()
		sim.Wait_To_Finish()

def Sample_Run():
	import robots
	
	pop_size = 10
	generator_fcn = robots.Quadruped
	fitness_fcn = Max_Y
	gens = 100
	
	evolver = AFPO(pop_size,generator_fcn,fitness_fcn,development_layers=1,max_generations=gens)
	
	best = evolver.Evolve()
	print len(best)
	Show(best)

if __name__ == "__main__":
	Sample_Run()

