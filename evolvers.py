from pyrosim import PYROSIM
from operator import itemgetter
import random

EVAL_TIME = 500
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
		sensor_data = {}

		for offset in range(0,len(self.population),NUM_IN_PARALLEL):
			sims = [0]*NUM_IN_PARALLEL
			for i in range(NUM_IN_PARALLEL):
				sims[i] = PYROSIM(playBlind=True, evalTime = self.eval_time)
				indv_to_send = self.population[i+offset]['genome']
				indv_to_send.Send_To_Simulator(sims[i],eval_time=self.eval_time)
				sims[i].Start()
			
			for i in range(NUM_IN_PARALLEL):
				sims[i].Wait_To_Finish()
				sensor_data[i+offset] = sims[i].Get_Results()

		return sensor_data

	def Sort_Population(self):
		self.population.sort(key=itemgetter('fitness') ,reverse=self.maximize)

	def Evaluate_Population(self):
		sensor_data = self.Send_Population_To_Simulator()
		for i in sensor_data:
			self.population[i]['fitness'] = self.fitness_fcn(sensor_data[i])
		
	def Mutate_And_Copy_Individual(self,index):
		return self.population[i].Mutate_And_Copy_Individual()	

	def Remove_Individual(self,index):
		del sel.population[index]


class AFPO(Evolver):
	def __init__(self,*args,**kwargs):
		super(AFPO,self).__init__(*args,**kwargs)
		

	def Add_Random_Individual(self):
		super(AFPO,self).Add_Random_Individual()
		self.population[-1]['age'] = 0
		self.population[-1]['is_dominated'] = False

	def Add_Individual(self,genome,age):
		super(AFPO,self).Add_Individual(genome)
		self.population[-1]['age'] = age
		self.population[-1]['is_dominated'] = False

	def Age_Population(self):
		for g in self.population:
			g['age'] += 1
	def Cull_Dominated(self):
		pop_length = len(self.population)
		for i in range(pop_length-1,-1,-1):
			if self.population[i]['is_dominated']:
				del self.population[i]


	def Determine_If_Dominated(self):
		for i in range(len(self.population)):
			indv_1 = self.population[i]
			if not indv_1['is_dominated']:
				for j in range(len(self.population)):
					if not self.population[j]['is_dominated'] and not(j==i):
						indv_2 = self.population[j]

						indv_1_is_younger = indv_1['age'] < indv_2['age']
						if self.maximize:
							indv_1_is_fitter = indv_1['fitness'] > indv_2['fitness']
						else:
							indv_1_is_fitter = indv_1['fitness'] < indv_2['fitness']

						if indv_1['age'] == indv_2['age'] and indv_1['fitness'] == indv_2['fitness']:
							if indv_1['ID'] < indv_2['ID']:
								indv_2['is_dominated'] = True
							else:
								indv_1['is_dominated'] = True
						elif indv_1_is_fitter and indv_1_is_younger:
							indv_2['is_dominated'] = True
						elif not(indv_1_is_fitter) and not(indv_1_is_younger):
							indv_1['is_dominated'] = True

	def Evolve(self):
		best = {}
		for i in range(self.max_generations):
			best[i] = self.Evolve_For_One_Generation()

		return best

	def Evolve_For_One_Generation(self):
		self.Evaluate_Population()

		self.Determine_If_Dominated()

		self.Cull_Dominated()

		self.Sort_Population()
		num_survivors = len(self.population)

		print self.generation, self.population[0]['fitness'], self.population[0]['age'],num_survivors
 		

		self.Age_Population()

		self.Fill_Population()

		self.Add_Random_Individual()

		self.Make_All_Non_Dominated()
 		
		self.generation += 1

		return self.population[0:num_survivors]


	def Fill_Population(self):
		num_survivors = len(self.population)
		for i in range(num_survivors,self.max_population_size-1):
			r = random.randint(0,num_survivors-1)
			mutant = self.population[r]['genome'].Copy_And_Mutate()
			age = self.population[r]['age']
			self.Add_Individual(mutant, age)

	def Make_All_Non_Dominated(self):
		for p in self.population:
			p['is_dominated'] = False

	def Sort_Population(self):
		self.population.sort(key=itemgetter('is_dominated') ,reverse=self.maximize)
		super(AFPO,self).Sort_Population()
		


def Max_XY(sensor_data):
	POS_SENSOR = 4
	Y_DIR = 1
	return sensor_data[POS_SENSOR,1,EVAL_TIME-1]+sensor_data[POS_SENSOR,0,EVAL_TIME-1]
def Max_Y(sensor_data):
	POS_SENSOR = 4
	Y_DIR = 1
	return sensor_data[POS_SENSOR,1,EVAL_TIME-1]


def Sample_Run():
	import robots
	import numpy as np
	pop_size = 50
	generator_fcn = robots.Quadruped
	fitness_fcn = Max_Y
	gens = 100
	N_SHOWS = 3
	evolver = AFPO(pop_size,generator_fcn,fitness_fcn,development_layers=4,max_generations=gens)
	evolver.Evaluate_Population()
	evolver.Determine_If_Dominated()
	
	best = evolver.Evolve()

	for i in range(0,gens,gens/N_SHOWS):
		robot_list = best[i]
		IDs = [0,0,0,0]
		sim = PYROSIM(playBlind=False,playPaused=False,evalTime=evolver.eval_time,xyz=(0.,-5.,4.),hpr=(90.0,-25.,0.0))
		N = len(robot_list)
		if N>5:
			N=5
		xVec = np.linspace(-N/2,N/2,num=N)
		for i in range(N):
			robot = robot_list[i]
			IDs = robot['genome'].Send_To_Simulator(sim,x_offset=xVec[i], objID=IDs[0],jointID=IDs[1],sensorID=IDs[2],neuronID=IDs[3])
		sim.Start()
		sim.Wait_To_Finish()

if __name__ == "__main__":
	Sample_Run()

