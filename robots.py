import networks
import subprocess
import simObjects
from pyrosim import PYROSIM
import copy
import math
import tree

CREATE_NETWORK = -1
BOX = 0
CYLINDER = 1
JOINT = 2
SENSOR = 3
MOTOR_SPEED = .25

class Robot(object):
	def __init__(self, motor_speed=MOTOR_SPEED,color=[1.0,1.0,1.0]):
		self.body_parts=[]
		self.joints=[]
		self.sensors = []
		self.network = False
		self.motor_speed = motor_speed
		self.color = self.r,self.g,self.b = color

	def Add_Network(self,network):
		self.network = network

	def Send_To_Simulator(self,sim,x_offset=0.,y_offset=0.,z_offset=0.,eval_time=200,
						objID=0,jointID=0,sensorID=0,neuronID=0,send_network=True):
		num_body_parts = len(self.body_parts)
		num_joints = len(self.joints)
		num_sensors = len(self.sensors)
		last_neuronID = neuronID

		for bp in self.body_parts:
			bp.Send_To_Simulator(sim,x_offset=x_offset,y_offset=y_offset,
										z_offset=z_offset,ID_offset=objID)
		for j in self.joints:
			j.Send_To_Simulator(sim,x_offset=x_offset,y_offset=y_offset,
								ID_offset=jointID,object_ID_offset=objID)
		for s in self.sensors:
			s.Send_To_Simulator(sim,ID_offset=sensorID,object_ID_offset=objID)

		if send_network:
			self.network.Send_To_Simulator(sim,neuron_offset=neuronID,joint_offset=jointID,sensor_offset=sensorID)
			last_neuronID += self.network.total_neurons

		return objID+num_body_parts,jointID+num_joints,sensorID+num_sensors,last_neuronID


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

	def Add_Ray_Sensor(self, **kwargs):
		sensor = simObjects.RaySensor(**kwargs)
		self.sensors.append(sensor)
	def Add_Position_Sensor(self,**kwargs):
		sensor = simObjects.PositionSensor(**kwargs)
		self.sensors.append(sensor)
	def Play(self, T=100):
		sim = PYROSIM(playPaused=False,playBlind=False,evalTime=T)
		self.Send_To_Simulator(sim)
		sim.Start()

	def Copy_And_Mutate(self,variable=-1,sigma=-1):
		mutant = copy.deepcopy(self)
		mutant.Mutate_Network(variable=variable,sigma=sigma)
		return mutant

	def Mutate_Network(self,variable=-1,sigma=-1):
		if variable<1 and variable>0:
			self.network.Mutate_p(p=variable,sigma=sigma)
		elif variable>=1:
			self.network.Mutate_n(n=variable,sigma=sigma)
		else:
			self.network.Mutate_p(p=1./float(len(self.network.synapses)),sigma=sigma)
class NPed(Robot):
	def __init__(self,x=0,y=0,z=0.3,num_legs=4,body_length=0.5,body_height=0.1,color=[0,0,0],network=False,z_incr=0.05,development_layers=1): 
		super(NPed,self).__init__(color = color)
		self.pos = self.x,self.y,self.z = x,y,z
		self.body_length = body_length
		self.body_height = body_height
		
		self.z_incr = z_incr
		self.leg_length = self.z
		self.radius = .5*self.body_height
		self.num_legs = num_legs
		self.body_ID = 0
		self.joint_ID = 0
		self.sensor_ID = 0
		self.development_layers = development_layers
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
								z=self.z+self.z_incr, n1=-leg_pos[1],n2=leg_pos[0],n3=0,
								speed=self.motor_speed)
			self.Add_Hinge_Joint(ID=knee_ID,firstObjectID=thigh_ID,secondObjectID=calf_ID,
								x=leg_pos[0]*l2+self.x,
								y=leg_pos[1]*l2+self.y,
								z=self.z+self.z_incr,n1=-leg_pos[1],n2=leg_pos[0],n3=0,
								speed=self.motor_speed)
			self.Add_Touch_Sensor(ID=sensor_ID,object_ID=calf_ID)
			sensor_ID+= 1
		self.Add_Position_Sensor(ID=sensor_ID,object_ID=body_ID)
		sensor_ID+=1

		self.body_ID = body_ID
		self.sensor_ID = sensor_ID
		self.joint_ID = joint_ID


	def Add_Random_Network(self):
		self.network = networks.LayeredNetwork(num_sensors=self.num_legs, hidden_per_layer=self.num_legs*2,num_layers=2,num_motors=self.num_legs*2, 
												development_layers=self.development_layers, back_connections=0,motor_recurrence=0,hidden_recurrence=0)

	def Send_To_Simulator(self,sim, eval_time, x_offset=0,y_offset=0,z_offset=0,objID=0,jointID=0,sensorID=0,neuronID=0,send_network=True):
		IDs = super(NPed,self).Send_To_Simulator(sim,x_offset=x_offset,y_offset=y_offset, z_offset=z_offset,
												objID=objID,jointID=jointID,sensorID=sensorID)
		last_objID = IDs[0]
		last_jointID = IDs[1]
		last_sensorID = IDs[2]
		last_neuronID = neuronID
		##### SEND NETWORK ###############################
		if send_network:
			self.network.Send_To_Simulator(sim,neuron_offset=neuronID,sensor_offset=sensorID,joint_offset=jointID,eval_time=eval_time)
			last_neuronID += self.network.total_neurons

		return last_objID,last_jointID,last_sensorID,last_neuronID

	def Get_Adj_Matrix(self):
		return self.network.Get_Adj_Matrix()

	def Change_Color(self, color):
		for part in self.body_parts:
			part.r = color[0]
			part.g = color[1]
			part.b = color[2]
			
class Quadruped(NPed):
	def __init__(self,*args,**kwargs):
		super(Quadruped,self).__init__(num_legs=4,*args,**kwargs)

class Treebot(Robot):
	def __init__(self, num_children=2,max_depth=1, branch_length=1,color=(1,0,0),development_layers=1):
		super(Treebot,self).__init__()

		self.branch_length = branch_length
		self.radius = branch_length/10.
		self.color = color
		self.r,self.g,self.b = color
		self.tree = tree.Sym_Tree(num_children=num_children,current_depth=0,max_depth=max_depth,
			branch_length=branch_length,
			base_position=[0.,0.,0.5],lo_angle=-math.pi/4,hi_angle=math.pi/4,global_angle=0,node_ID=0)

		self.ray_sensor_ID = 0

		self.Init_Parts(self.tree)

		#self.network = networks.NM_TreeNetwork(self.tree,num_layers=1,hidden_per_layer=1)
		#print len(self.joints)

	def Init_Parts(self,tree):
		pos = tree.Get_Center()
		orientation = tree.Get_Orientation()
		node_ID = tree.node_ID
		parent_ID = tree.parent_ID


		self.Add_Cylinder(ID=node_ID,x=pos[0],y=pos[1],z=pos[2],
					r1=orientation[0],r2=orientation[1],r3=orientation[2],
					length=self.branch_length,
					radius=self.radius,r=self.r,g=self.g,b=self.b)



		if tree.depth==0:
			lo = tree.lo_angle*3
			hi = tree.hi_angle*3
		else:
			lo = 2*tree.lo_angle/float(tree.depth)
			hi = 2*tree.hi_angle/float(tree.depth)


		self.Add_Hinge_Joint(ID=node_ID,firstObjectID=node_ID,secondObjectID=parent_ID,
			x=tree.base_position[0],y=tree.base_position[1],
			z=tree.base_position[2],n1=0,n2=0,n3=-1,lo=lo,hi=hi,
			speed=MOTOR_SPEED)
		# self.Add_Hinge_Joint(ID=node_ID, firstObjectID=node_ID,secondObjectID=parent_ID,
		# 	x=0.0,y=0.0,z=0.5,n1=1,n2=0,n3=0,lo=-1,hi=1,speed=MOTOR_SPEED)
		if tree.is_leaf:
			self.Add_Ray_Sensor(ID=self.ray_sensor_ID, object_ID=node_ID, x=pos[0],y=pos[1],z=pos[2],
									r1=orientation[0],r2=orientation[1],r3=orientation[2])
			self.ray_sensor_ID += 1
		else:
			for child in tree.children:
				self.Init_Parts(child)

	@classmethod
	def Non_Modular(cls, network=False):
		t = cls()
		for joint in t.joints:
			if joint.ID > 0:
				joint.lo = 0
				joint.hi = 0
		#make network from sensors:0,1 to motor:0 with 2 hidden layers each with 4 neurons
		#Back connections are on
		#Motor recurrence is on
		#M
		if network:
			t.network = network
		else:
			t.network = networks.Layered_Network([0,1],[0],[8,8],hidden_recurrence=True,motor_recurrence=True,back_connections=True)
		return t
	@classmethod
	def Modular(cls, network = False):
		t = cls()
		for joint in t.joints:
			if joint.ID == 0:
				joint.lo = 0
				joint.hi = 0

		if network:
			t.network = network
		else:
			net1 = networks.Layered_Network([0],[1],[4,4],motor_recurrence=True,hidden_recurrence=True,back_connections=True)
			net2 = networks.Layered_Network([1],[2],[4,4],motor_recurrence=True,hidden_recurrence=True,back_connections=True)
			t.network = networks.Network.Combine(net1,net2)
		return t

def _Test_Tree():

	T = 1000
	sim = PYROSIM(playPaused=False, playBlind=False, evalTime=T,xyz=[0,0,5],hpr=[90,-90,0])
	#sim = PYROSIM(playPaused=False, playBlind=False, evalTime=T, xyz=[-5,0,2], hpr=[0,-20,0])
	t = Treebot()
	t.Send_To_Simulator(sim)
	sim.Start()
	sim.Wait_To_Finish()
	data = sim.Get_Results()
	#print t.network.adj_matrix[:,:,0]

def _Test_Mutate_Quad(sim):
	quad = Quadruped(color=[0.4,0.4,1.0])
	IDs = quad.Send_To_Simulator(sim,eval_time=sim.evaluationTime)
	newQuad = quad.Copy_And_Mutate(variable=.99,sigma=5)
	newQuad.Send_To_Simulator(sim, eval_time=sim.evaluationTime,objID=IDs[0],jointID=IDs[1],sensorID=IDs[2],neuronID=IDs[3])
	sim.Start()
	sim.Wait_To_Finish()

def _Test_Robot_Army(sim):
	import numpy as np
	N = 5
	IDs = [0,0,0,0]
	nped = Quadruped(color=[1.0,.4,.5])

	for x in np.linspace(-N,N,num=N):
		for y in np.linspace(-1,N*2,num=N*2):
			IDs = nped.Send_To_Simulator(sim,x_offset=x,y_offset=y,objID=IDs[0],jointID=IDs[1],sensorID=IDs[2],neuronID=IDs[3])

	sim.Start()

def _Test_Draw():
	T = 1000
	quad = Quadruped()
	sim = PYROSIM(playPaused=False,playBlind=True,evalTime=T)
	quad.Send_To_Simulator(sim)
	sim.Start()
	sim.Wait_To_Finish()
	data = sim.Get_Results()
	print data[4,1,T-1]

	sim2 = PYROSIM(playPaused=False,playBlind=False,evalTime=T)
	quad.Send_To_Simulator(sim2)
	sim2.Start()
	sim2.Wait_To_Finish()
	data = sim2.Get_Results()
	print data[4,1,T-1]

	mutant = quad.Copy_And_Mutate(variable=.99,sigma=5)
	sim3 = PYROSIM(playPaused=False,playBlind=False,evalTime=T)
	IDs = quad.Send_To_Simulator(sim3)
	print IDs
	IDs = mutant.Send_To_Simulator(sim3, objID=IDs[0],jointID=IDs[1],sensorID=IDs[2],neuronID=IDs[3])
	sim3.Start()
	sim3.Wait_To_Finish()
	data = sim3.Get_Results()
	print data[4,1,T-1], data[9,1,T-1]



if __name__ == "__main__":
	#_Test_Draw()
	import numpy as np
	import environments
	import fitness_functions as ff
	t = Treebot.Modular()
	#t = Treebot.Non_Modular()
	#t = Treebot()

	sim = PYROSIM(playPaused=True,playBlind=False,evalTime=100)
	offset = t.Send_To_Simulator(sim, eval_time=100)
	env = environments.Cluster_Env.Bi_Sym(3,2,4,2)
	env.Send_To_Simulator(sim,offset[0])
	sim.Start()
	sim.Wait_To_Finish()
	results = sim.Get_Results()
	#nfitne = Collect_Color(results, env)
	#print fitness
	print ff.Treebot(results,env)

	# T = 200
	# sim = PYROSIM(playPaused=True, playBlind=False, evalTime=T)
	# mybot = Quadruped(color=[1.0,0.,0.])
	# mybot.Send_To_Simulator(sim,T)
	# sim.Start()
	# objID = 0
	# jointID = 0
	# sensorID = 0
	# neuronID = 0
	
	# N = 10
	# Start = 0
	# incr = 1.5
	# index = 0
	# #Robot_Army(sim)
	#_Test_Mutate_Quad(sim)
	# _Test_Tree()

