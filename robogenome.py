
BODY = 0
BRAIN = 1
TYPE = 'type'
PARAMS = 'paramaters'
class Genome(object):
	def __init__(self):
		self.body_parts = {}
		self.joints = {}
		self.brain_parts = {}
		self.senors = {}

		self.body_index = 0
		self.brain_index = 0
		self.num_joints = 0
		self.num_body_parts = 0
		self.num_sensors = 0
	def Add_Part(self,which,part_type,part_params={}):
		if which==BODY:
			self.body_parts[self.body_index] = {}
			self.body_parts[self.body_index][TYPE] = part_type
			self.body_parts[self.body_index][PARAMS] = part_params
			self.body_index += 1
		elif which==BRAIN:
			self.brain_parts[self.brain_index] = {}
			self.brain_parts[self.brain_index][TYPE] = part_type
			self.brain_parts[self.brain_index][PARAMS] = part_params
			self.brain_index += 1

	def Add_Body_Part(self,part_type,part_params={}):
		self.body_parts[self.body_index] = {}
		self.body_parts[self.body_index][TYPE] = part_type
		self.body_parts[self.body_index][PARAMS] = part_params
		self.body_index += 1


	def Add_Brain_Part(self,part_type,part_params={}):
		self.Add_Part(BRAIN,part_type,part_params)


	def Add_Cylinder(self, part_params={}):
		pass
	

	def Print(self):
		print 'body'
		for key in self.body_parts:
			print '   ',key, self.body_parts[key]
		print '-----------------'
		print 'brain'
		for key in self.brain_parts:
			print '	  ',key, self.brain_parts[key]

	def Get_Part(self,which,index):
		if which==BODY:
			return self.body_parts[index][TYPE],self.body_parts[index][PARAMS]
		elif which==BRAIN:
			return self.brain_parts[index][TYPE],self.brain_parts[index][PARAMS]
	def Get_Body_Part(self,index):
		part_type, part_params = self.Get_Part(BODY,index)
		return part_type, part_params
	def Get_Brain_Part(self,index):
		part_type, part_params = self.Get_Part(BRAIN,index)
		return part_type, part_params

if __name__=="__main__":
	gen = Genome()
	gen.Add_Body_Part(part_type=0,part_params={'range':'.'})
	gen.Print()
	for i in gen.body_parts:
		x,y = gen.Get_Body_Part(i)
	print x,y
	#print x,y
