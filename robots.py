import networks
import subprocess
import simObjects
from pyrosim import PYROSIM
import copy
import math


CREATE_NETWORK = -1
BOX = 0
CYLINDER = 1
JOINT = 2
SENSOR = 3
MOTOR_SPEED = 0.75

class Robot(object):
	def __init__(self):
		self.body_parts=[]
		self.joints=[]
		self.sensors = []
		self.network = False
		
	def Send_To_Simulator(self,sim,x_offset=0.,y_offset=0.,z_offset=0.,
						objID=0,jointID=0,sensorID=0,neuronID=0,send_network=True):
		num_body_parts = len(self.body_parts)
		num_joints = len(self.joints)
		num_sensors = len(self.sensors)


		for bp in self.body_parts:
			bp.Send_To_Simulator(sim,x_offset=x_offset,y_offset=y_offset,
										z_offset=z_offset,ID_offset=objID)
		for j in self.joints:
			j.Send_To_Simulator(sim,x_offset=x_offset,y_offset=y_offset,
								ID_offset=jointID,object_ID_offset=objID)
		for s in self.sensors:
			s.Send_To_Simulator(sim,ID_offset=sensorID,object_ID_offset=objID)

		return objID+num_body_parts,jointID+num_joints,sensorID+num_sensors

	def Add_Cylinder(self, **kwargs):
		cylinder = simObjects.Cylinder(**kwargs)
		self.body_parts.append(cylinder)


	def Add_Box(self, **kwargs):
		box = simObjects.Box(**kwargs)
		self.body_parts.append(box)

	def Add_Hinge_Joint(self, **kwargs):
		joint = simObjects.HingeJoint(**kwargs)
		self.joints.append(joint)

	def Add_Touch_Sensor(self,**kwargs):
		sensor = simObjects.TouchSensor(**kwargs)
		self.sensors.append(sensor)

	def Add_Position_Sensor(self,**kwargs):
		sensor = simObjects.PositionSensor(**kwargs)
		self.sensors.append(sensor)

class NPed(Robot):
	def __init__(self,x=0,y=0,z=0.3,num_legs=4,body_length=0.5,body_height=0.1,color=[0,0,0],network=False,z_incr=0.05): 
		super(NPed,self).__init__()
		self.pos = self.x,self.y,self.z = x,y,z
		self.body_length = body_length
		self.body_height = body_height
		self.color = self.r,self.g,self.b = color
		self.z_incr = z_incr
		self.leg_length = self.z
		self.radius = .5*self.body_height
		self.num_legs = num_legs
		self.body_ID = 0
		self.joint_ID = 0
		self.sensor_ID = 0
		self.Add_Body()


		if not(network):
			self.Add_Random_Network()
		else:
			self.network = network.Send_To_Simulator()

	def Add_Body(self):
		object_ID = 0
		body_ID = 0
		sensor_ID = 0
		joint_ID = 0

		self.Add_Box(ID=body_ID,x=self.x,y=self.y,z=self.z+self.z_incr,
						length=self.body_length,width=self.body_length,
						height=self.body_height,r=self.r,g=self.g,b=self.b)
		object_ID += 1

		delta = 0.
		for i in range(self.num_legs):
			leg_pos = (math.cos(delta),math.sin(delta))
			delta += math.pi/((self.num_legs)/2.0)

			l1,l2 = (self.body_length+self.leg_length)/2., self.body_length/2.+self.leg_length

			thigh_ID = object_ID
			object_ID += 1
			calf_ID = object_ID
			object_ID += 1
			hip_ID = joint_ID
			joint_ID += 1
			knee_ID = joint_ID
			joint_ID += 1

			self.Add_Cylinder(ID=thigh_ID,x=leg_pos[0]*l1+self.x,y=leg_pos[1]*l1+self.y,
								z=self.z+self.z_incr,r1=leg_pos[0],r2=leg_pos[1],r3=0,
								length=self.leg_length, radius=self.radius, r=self.r,
								g=self.g, b=self.b)

			self.Add_Cylinder(ID=calf_ID,x=leg_pos[0]*l2+self.x,y=leg_pos[1]*l2+self.y,
								z=self.z/2.+self.z_incr, r1=0,r2=0,r3=1,length=self.leg_length,
								radius=self.radius,r=self.r,g=self.g,b=self.b)

			self.Add_Hinge_Joint(ID=hip_ID,firstObjectID=body_ID,secondObjectID=thigh_ID,
								x=leg_pos[0]*self.body_length/2.+self.x, 
								y=leg_pos[1]*self.body_length/2.+self.y,
								z=self.z+self.z_incr, n1=-leg_pos[1],n2=leg_pos[0],n3=0,speed=MOTOR_SPEED)
			self.Add_Hinge_Joint(ID=knee_ID,firstObjectID=thigh_ID,secondObjectID=calf_ID,
								x=leg_pos[0]*l2+self.x,y=leg_pos[1]*l2+self.y,
								z=self.z+self.z_incr,n1=-leg_pos[1],n2=leg_pos[0],n3=0,
								speed=MOTOR_SPEED)
			self.Add_Touch_Sensor(ID=sensor_ID,object_ID=calf_ID)
			sensor_ID+= 1
		self.Add_Position_Sensor(ID=sensor_ID,object_ID=body_ID)
		sensor_ID+=1

		self.body_ID = body_ID
		self.sensor_ID = sensor_ID
		self.joint_ID = joint_ID

	def Add_Network(self,network):
		self.network = network

	def Add_Random_Network(self):
		#self.network = networks.LayeredNetwork(num_sensors=self.num_legs,hidden_per_layer=self.num_legs*2,num_motors=self.num_legs*2)
		self.network=networks.LayeredNetwork(num_sensors=self.num_legs,num_motors=self.num_legs*2,num_layers=1,hidden_per_layer=self.num_legs*2)
	def Send_To_Simulator(self,sim, x_offset=0,y_offset=0,z_offset=0,objID=0,jointID=0,sensorID=0,neuronID=0,send_network=True):
		IDs = super(NPed,self).Send_To_Simulator(sim,x_offset=x_offset,y_offset=y_offset, z_offset=z_offset,
												objID=objID,jointID=jointID,sensorID=sensorID)
		last_objID = IDs[0]
		last_jointID = IDs[1]
		last_sensorID = IDs[2]
		last_neuronID = neuronID
		##### SEND NETWORK ###############################
		if send_network:
			self.network.Send_To_Simulator(sim,neuron_offset=neuronID,sensor_offset=sensorID,joint_offset=jointID)
			last_neuronID += self.network.total_neurons

		return last_objID,last_jointID,last_sensorID,last_neuronID

	def Mutate_Network(self,variable=-1,sigma=-1):
		if variable<1 and variable>0:
			self.network.Mutate_p(p=variable,sigma=sigma)
		elif variable>=1:
			self.network.Mutate_n(n=variable,sigma=sigma)
		else:
			self.network.Mutate_p(sigma=sigma)


	def Copy_And_Mutate(self,variable=-1,sigma=-1):
		mutant = copy.deepcopy(self)
		mutant.Mutate_Network(variable=variable,sigma=sigma)
		return mutant

	def Get_Adj_Matrix(self):
		return self.network.Get_Adj_Matrix()

class Quadruped(NPed):
	def __init__(self,*args,**kwargs):
		super(Quadruped,self).__init__(num_legs=4,*args,**kwargs)


def _Test_Mutate_Quad(sim):
	quad = Quadruped(color=[0.4,0.4,1.0])
	IDs = quad.Send_To_Simulator(sim)
	newQuad = quad.Copy_And_Mutate(variable=.99,sigma=5)
	newQuad.Send_To_Simulator(sim, objID=IDs[0],jointID=IDs[1],sensorID=IDs[2],neuronID=IDs[3])
	sim.Start()
def _Test_Robot_Army(sim):
	import numpy as np
	N = 5
	IDs = [0,0,0,0]
	nped = Quadruped(color=[1.0,.4,.5])

	for x in np.linspace(-N,N,num=N):
		for y in np.linspace(-1,N*2,num=N*2):
			IDs = nped.Send_To_Simulator(sim,x_offset=x,y_offset=y,objID=IDs[0],jointID=IDs[1],sensorID=IDs[2],neuronID=IDs[3])

	sim.Start()


if __name__ == "__main__":
	
	import numpy as np

	T = 500
	sim = PYROSIM(playPaused=False, playBlind=False, evalTime=T)
	objID = 0
	jointID = 0
	sensorID = 0
	neuronID = 0
	
	N = 10
	Start = 0
	incr = 1.5
	index = 0
	#Robot_Army(sim)
	_Test_Mutate_Quad(sim)

