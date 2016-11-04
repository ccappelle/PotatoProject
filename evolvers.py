from pyrosim import PYROSIM
import random

EVAL_TIME = 100
NUM_IN_PARALLEL = 10
class Evolver(object):
	def __init__(self,max_pop_size,generator_fcn,fitness_fcn={},evalTime=EVAL_TIME):
		
		self.pop = {}
		self.max_pop_size = max_pop_size
		self.fitness = []
		self.generator_fcn = generator_fcn
		self.fitness_fcn = fitness_fcn
		self.evalTime = evalTime
		for i in range(self.max_pop_size):
			self.Add_Random_Individual()


	def Add_Indvidual(self,indv):
		self.pop.append(indv)
		self.fitness.append(False)

	def Add_Random_Individual(self):
		self.pop.append(self.generator_fcn())
		self.fitness.append(0)
 
	def Send_Pop_To_Simulator(self):
		sensor_data = {}

		for offset in range(0,len(self.pop),NUM_IN_PARALLEL):
			sims = [0]*NUM_IN_PARALLEL
			for i in range(NUM_IN_PARALLEL):
				sims[i] = PYROSIM(playBlind=True, evalTime = self.evalTime)
				self.pop[i+offset].Send_To_Simulator(sims[i])
				sims[i].Start()
			
			for i in range(NUM_IN_PARALLEL):
				sims[i].Wait_To_Finish()
				sensor_data[i+offset] = sims[i].Get_Results()

		return sensor_data
	def Evaluate_Pop(self):
		sensor_data = self.Send_Pop_To_Simulator()
		for i in sensor_data:
			self.fitness[i] = self.fitness_fcn(sensor_data[i])
		
	def Mutate_And_Copy_Individual(self,index):
		return self.pop[i].Mutate_And_Copy_Individual()	

	def Remove_Individual(self):

class AFPO(Evolver):
	def __init__(self,**kwargs):
		super(AFPO,self).__init__(kwargs)
		self.age = []
		
	def Add_New_Individual(self):
		self.Add_Individual(age=0)

	def Add_Individual(self,age=0):
		self.age.append(age)
		super(AFPO,self).Add_Individual()

	def Fill_Pop(self):
		for i in range(len(self.pop),max_pop_size-1):
			r = random.randint(0,len(self.pop)-1)
			mutant = self.pop[r].Copy_And_Mutate()
			self.Add_Individual()

def _Max_Y(sensor_data):
	POS_SENSOR = 4
	Y_DIR = 1
	return sensor_data[POS_SENSOR,1,EVAL_TIME-1]

if __name__ == "__main__":
	import robots
	pop_size = 100
	generator_fcn = robots.Quadruped
	fitness_fcn = _Max_Y
	evolver = Evolver(pop_size,generator_fcn,fitness_fcn)
	evolver.Evaluate_Pop()
	print evolver.fitness
	evolver.Mutate_Pop()
	evolver.Evaluate_Pop()
	print evolver.fitness

