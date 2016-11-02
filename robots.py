import networks
import subprocess
import robogenome
from pyrosim import PYROSIM
import copy
import math


CREATE_NETWORK = -1
BOX = 0
CYLINDER = 1
JOINT = 2
SENSOR = 3

class Robot(object):
	def __init__(self):
		self.genome=robogenome.Genome()
		self.num_body_parts = 0
		self.num_joints = 0
		self.num_sensors = 0
		self.num_neurons = 0
		
	def Send_To_Simulator(self,sim,x_offset=0.,y_offset=0.,z_offset=0.,
						objID=0,jointID=0,sensorID=0,neuronID=0,send_network=True):
		num_objects = 0
		num_sensors = 0
		num_joints = 0
		num_neurons = 0
		for i in self.genome.body_parts:
			part_type, part_params = self.genome.Get_Body_Part(i)
			if 'ID' not in part_params:
				if part_type == BOX or part_type == CYLINDER:
					part_params['ID'] = objID
				elif part_type == JOINT:
					part_params['ID'] = jointID
				elif part_type == SENSOR:
					part_params['ID'] = sensorID

			if part_type==BOX:
				part_params['ID'] += objID
				sim.Send_Box(**part_params)
				part_params['ID'] -= objID
				num_objects += 1

			elif part_type==CYLINDER:
				part_params['ID'] += objID
				sim.Send_Cylinder(**part_params)
				part_params['ID'] -= objID
				num_objects += 1

			elif part_type==JOINT:
				part_params['ID'] += jointID
				sim.Send_Joint(**part_params)
				part_params['ID'] -= jointID
				num_joints += 1

			elif part_type==SENSOR:
				part_params['ID'] += sensorID
				sim.Send_Joint(**part_params)
				part_params['ID'] -= sensorID
				num_sensors += 1


		return objID+num_objects,jointID+num_joints,sensorID+num_sensors,neuronID+num_neurons

class NPed(object):
	def __init__(self,x=0,y=0,z=0.3,num_legs=4,body_length=0.5,body_height=0.1,color=[0,0,0],network=CREATE_NETWORK,z_incr=0.05): 
		self.pos = self.x,self.y,self.z = x,y,z
		self.body_length = body_length
		self.body_height = body_height
		self.color = self.r,self.g,self.b = color
		self.z_incr = z_incr
		self.leg_length = self.z
		self.radius = .5*self.body_height
		self.network = network
		self.num_legs = num_legs

		if self.network == CREATE_NETWORK:
			self.Add_Random_Network()


	def Add_Network(self,network):
		self.network = network

	def Add_Random_Network(self):
		self.network = networks.LayeredNetwork(num_sensors=self.num_legs,num_hidden=self.num_legs*2,num_motors=self.num_legs*2)

	def Send_To_Simulator(self,sim, objID=0,jointID=0,sensorID=0,neuronID=0,send_network=True):
		
		init_sensorID = sensorID
		init_jointID = jointID
		init_objID = objID
		#self.Send_Body()

		bodyID = objID
		objID += 1
		(r,g,b) = self.color

		#Body 
		sim.Send_Box(ID=bodyID, x=self.x,y=self.y,z=self.z+self.z_incr,
					length=self.body_length,width=self.body_length,
					height=self.body_height,r=self.r,g=self.g,b=self.b)

		#Auto asign legs based on how high the body is set to be

		delta = 0.
		num_legs = self.num_legs
		for i in range(num_legs):
			leg_x = math.cos(delta)
			leg_y = math.sin(delta)
			delta += math.pi/((num_legs)/2.0)
			bl_length1 = (self.body_length+self.leg_length)/2.
			bl_length2 = self.body_length/2.+self.leg_length

			thighID = objID
			objID += 1
			calfID = objID
			objID += 1
			#Thigh
			sim.Send_Cylinder(ID=thighID, x=leg_x*bl_length1+self.x,y=leg_y*bl_length1+self.y,
								z=self.z+self.z_incr,r1=leg_x,r2=leg_y,r3=0,length=self.leg_length,
								radius=self.radius,r=self.r,g=self.g,b=self.b)
			
			#Calf
			sim.Send_Cylinder(ID=calfID, x=leg_x*bl_length2+self.x,y=leg_y*bl_length2+self.y,
								z=self.z/2.+self.z_incr,r1=0,r2=0,r3=1, length=self.z,radius=self.radius,
								r=self.r,g=self.g,b=self.b)

			#Hip joint
			sim.Send_Joint(ID=jointID, firstObjectID=bodyID, secondObjectID=thighID, 
							x=leg_x*self.body_length/2.+self.x,y=leg_y*self.body_length/2.+self.y,z=self.z+self.z_incr,
							n1=-leg_y,n2=leg_x,n3=0)
			jointID+=1

			#Knee Joint
			sim.Send_Joint(ID=jointID, firstObjectID=thighID, secondObjectID=calfID, 
							x=leg_x*bl_length2+self.x,y=leg_y*bl_length2+self.y,z=self.z+self.z_incr,
							n1=-leg_y,n2=leg_x,n3=0)
			jointID+=1

			#Sensor on feet
			sim.Send_Touch_Sensor(ID=sensorID, objectIndex=calfID)
			sensorID += 1
		
		#Send a position sensor attached to the body
		sim.Send_Position_Sensor(ID=sensorID,objectIndex=bodyID)
		sensorID +=1

		last_sensorID = sensorID
		last_objID = objID
		last_jointID = jointID

		##### SEND NETWORK ###############################
		if send_network:

			#Sends a neural net to the simulator
			sensor_neuron_start = neuronID
			for sensor_index in range(self.network.num_sensors): #Send sensor neurons to sim
				sim.Send_Sensor_Neuron(ID=sensor_neuron_start+sensor_index,sensorID=sensor_index+init_sensorID)

			hidden_neuron_start = sensor_neuron_start + self.network.num_sensors
			for hidden_index in range(self.network.num_layers*self.network.num_hidden): #Send hidden neurons to sim
				sim.Send_Hidden_Neuron(ID=hidden_neuron_start+hidden_index)

			motor_neuron_start = hidden_neuron_start + self.network.num_hidden*self.network.num_layers
			for motor_index in range(self.network.num_motors): #Send motor neurons to sim
				sim.Send_Motor_Neuron(ID=motor_neuron_start+motor_index, jointID= init_jointID+motor_index)

			for i in range(self.network.total_neurons):
				for j in range(self.network.total_neurons):
					if not(self.network.adj_matrix[i,j]==0): #Connect neurons with synapses from network adj matrix
						sim.Send_Synapse( neuronID+i,neuronID+j,self.network.adj_matrix[i,j])

			last_neuronID = neuronID + self.network.total_neurons

		

		if send_network:
			return last_objID,last_jointID,last_sensorID,last_neuronID
		else:
			return last_objID,last_jointID,last_sensorID

	def Mutate_Network(self,var=-1,sigma=-1):
		if var<1 and var>0:
			self.network.Mutate_p(p=var,sigma=sigma)
		elif var>=1:
			self.network.Mutate_n(n=var,sigma=sigma)
		else:
			self.network.Mutate_p(sigma=sigma)


	def Copy_And_Mutate(self,var=-1,sigma=-1):
		mutant = copy.deepcopy(self)
		mutant.Mutate_Network(var=var,sigma=sigma)
		return mutant

	def Get_Adj_Matrix(self):
		return self.network.Get_Adj_Matrix()
class Quadruped(NPed):
	def __init__(self,*args,**kwargs):
		super(Quadruped,self).__init__(num_legs=4,*args,**kwargs)


if __name__ == "__main__":
	pass
	import numpy as np
	# sim = PYROSIM(playPaused=False,playBlind=False,evalTime = 500)
	# robo = Robot()
	# robo.genome.Add_Body_Part(BOX,{'ID':0,'x':4})
	# robo.Send_To_Simulator(sim)
	
	# sim.Start()

	#Test Simulation of multiple robots
	T = 1000
	sim = PYROSIM(playPaused=False, playBlind=False, evalTime=T)

	objID = 0
	jointID = 0
	sensorID = 0
	neuronID = 0
	pos_sensor_list = []
	N = 10
	for i in range(N): #Create N potatoes, each with a different random flavor
		color = np.random.rand(3)
		pedBot = NPed(x=i*1.5-N/2,num_legs=i,color=color)
		objID,jointID,sensorID,neuronID = pedBot.Send_To_Simulator(sim, objID=objID,jointID=jointID,sensorID=sensorID,neuronID=neuronID)
		pos_sensor_list.append(sensorID-1)

	sim.Start()
	sim.Wait_To_Finish()


	
	# gaitData={}
	# posData = np.zeros((3,T))
	# for i in range(4):
	# 	gaitData[i] = [0]*T
	# 	for t in range(T):
	# 		gaitData[i][t] = int(sim.dataFromPython[i,0,t])

	# for t in range(T):
	# 	for i in range(3):
	# 		posData[i,t] = sim.dataFromPython[4,i,t]
	# 	print posData[:,t]


