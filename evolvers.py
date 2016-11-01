
class Evolver(object):
	def __init__(self,max_pop_size,generator_fcn):
		self.pop = []
		self.max_pop_size = max_pop_size
		self.fitness = []
		self.generator_fcn = generator_fcn

		for i in range(self.max_pop_size):
			self.Add_Individual(generator_fcn)


	def Add_Individual(self,generator_fcn):
		self.pop.append(generator_fcn())
		self.fitness.append(0)


class AFPO(Evolver):
	def __init__(self,**kwargs):
		super(AFPO,self).__init__(kwargs)
		self.age = []
		pass

	def Add_Individual(self,generator_fcn):
		self.age.append(0)
		super(AFPO,self).Add_Individual(generator_fcn)


class HillClimber(Evolver):
	def __init__(self):
		pass


if __name__ == "__main__":
	pass
