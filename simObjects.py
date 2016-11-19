import math


class Shape(object):
	def __init__(self,ID=0,x=0,y=0,z=0,r=0.5,g=0.5,b=0.5):
		self.ID = ID
		self.x = x
		self.y = y
		self.z = z
		self.r,self.g,self.b = r,g,b

	def Get_kwargs(self,x_offset=0,y_offset=0,z_offset=0,ID_offset=0):
		kwargs = {}
		kwargs['ID'] = self.ID+ID_offset
		kwargs['x'] = self.x+x_offset
		kwargs['y'] = self.y+y_offset
		kwargs['z'] = self.z+z_offset
		kwargs['r'] = self.r
		kwargs['g'] = self.g
		kwargs['b'] = self.b

		return kwargs

class Cylinder(Shape):
	def __init__(self,ID=0,x=0, y=0, z=0, r1=0, r2=0, r3=1, length=1.0, radius=0.1, r=1, g=1, b=1):
		super(Cylinder,self).__init__(ID=ID,x=x,y=y,z=z,r=r,g=g,b=b)
		self.r1 = r1
		self.r2 = r2
		self.r3 = r3
		self.length = length
		self.radius = radius

	def Send_To_Simulator(self,sim,x_offset=0,y_offset=0,z_offset=0,ID_offset=0):
		kwargs = self.Get_kwargs(x_offset=x_offset,y_offset=y_offset,z_offset=z_offset,ID_offset=ID_offset)
		sim.Send_Cylinder(**kwargs)
		#print 'sent cylinder', kwargs
	def Get_kwargs(self,x_offset=0,y_offset=0,z_offset=0,ID_offset=0):
		kwargs = super(Cylinder,self).Get_kwargs(x_offset,y_offset,z_offset,ID_offset)
		kwargs['r1'] = self.r1
		kwargs['r2'] = self.r2
		kwargs['r3'] = self.r3
		kwargs['length'] = self.length
		kwargs['radius'] = self.radius

		return kwargs

class Box(Shape):
	def __init__(self,ID=0,x=0,y=0,z=0,length=0.1,width=0.1,height=0.1, r=0,g=0,b=0):
		super(Box,self).__init__(x=x,y=y,z=z,r=r,g=g,b=b)
		self.length = length
		self.width = width	
		self.height = height

	def Send_To_Simulator(self,sim,x_offset=0,y_offset=0,z_offset=0,ID_offset=0):
		kwargs = self.Get_kwargs(x_offset,y_offset,z_offset,ID_offset)
		sim.Send_Box(**kwargs)

	def Get_kwargs(self,x_offset=0,y_offset=0,z_offset=0,ID_offset=0):
		kwargs = super(Box,self).Get_kwargs(x_offset,y_offset,z_offset,ID_offset)
		kwargs['length'] = self.length
		kwargs['width'] = self.width
		kwargs['height'] = self.height

		return kwargs

class Joint(object):
	def __init__(self,ID=0,firstObjectID=0,secondObjectID=1,x=0,y=0,z=0):
		self.ID = ID
		self.firstObjectID = firstObjectID
		self.secondObjectID = secondObjectID
		self.x = x
		self.y = y
		self.z = z

	def Get_kwargs(self,x_offset=0,y_offset=0,z_offset=0,ID_offset=0,object_ID_offset=0):
		kwargs = {}
		kwargs['ID'] = self.ID + ID_offset
		kwargs['x'] = self.x+x_offset
		kwargs['y'] = self.y+y_offset
		kwargs['z'] = self.z+z_offset
		kwargs['firstObjectID'] = self.firstObjectID + object_ID_offset
		kwargs['secondObjectID'] = self.secondObjectID+object_ID_offset

		return kwargs

class HingeJoint(Joint):
	def __init__(self,ID=0,firstObjectID=0,secondObjectID=-1,x=0,y=0,z=0,n1=0,n2=0,n3=1,lo=-math.pi/4.0,hi=math.pi/4.0,speed=1.0):
		super(HingeJoint,self).__init__(ID=ID,firstObjectID=firstObjectID,secondObjectID=secondObjectID,
										x=x,y=y,z=z)
		self.n1 = n1
		self.n2 = n2
		self.n3 = n3
		self.lo = lo
		self.hi = hi
		self.speed=speed

	def Send_To_Simulator(self,sim,x_offset=0,y_offset=0,z_offset=0,object_ID_offset=0,ID_offset=0):
		kwargs = self.Get_kwargs(x_offset,y_offset,z_offset,ID_offset,object_ID_offset)
		sim.Send_Joint(**kwargs)
		#print 'sent joint', kwargs
	def Get_kwargs(self,x_offset=0,y_offset=0,z_offset=0,ID_offset=0,object_ID_offset=0):
		kwargs = super(HingeJoint,self).Get_kwargs(x_offset,y_offset,z_offset,ID_offset,object_ID_offset)
		if self.secondObjectID < 0:
			kwargs['secondObjectID'] = -1

		kwargs['lo'] = self.lo
		kwargs['hi'] = self.hi
		kwargs['n1'] = self.n1
		kwargs['n2'] = self.n2
		kwargs['n3'] = self.n3
		kwargs['speed'] = self.speed
		return kwargs

class Sensor(object):
	def __init__(self,ID=0,object_ID=0):
		self.ID= ID
		self.object_ID = object_ID

	def Get_kwargs(self,ID_offset=0,object_ID_offset=0):
		kwargs = {}
		kwargs['ID'] = self.ID+ID_offset
		kwargs['objectIndex'] = self.object_ID+object_ID_offset

		return kwargs

class LightSensor(Sensor):
	def Send_To_Simulator(self,sim,ID_offset=0,object_ID_offset=0):
		kwargs = self.Get_kwargs(ID_offset,object_ID_offset)
		sim.Send_Light_Sensor(**kwargs)

class PositionSensor(Sensor):
	def Send_To_Simulator(self,sim,ID_offset=0,object_ID_offset=0):
		kwargs = self.Get_kwargs(ID_offset,object_ID_offset)
		sim.Send_Position_Sensor(**kwargs)

class TouchSensor(Sensor):
	def Send_To_Simulator(self,sim,ID_offset=0,object_ID_offset=0):
		kwargs = self.Get_kwargs(ID_offset,object_ID_offset)
		sim.Send_Touch_Sensor(**kwargs)

class RaySensor(Sensor):
	def __init__(self,ID=0,object_ID=0,x=0,y=0,z=0,r1=1,r2=0,r3=0):
		super(RaySensor,self).__init__(ID=ID,object_ID=object_ID)
		self.x= x
		self.y= y
		self.z = z
		self.r1 = r1
		self.r2 = r2
		self.r3 = r3

	def Get_kwargs(self,ID_offset=0,object_ID_offset=0,x_offset=0,y_offset=0,z_offset=0):
		kwargs = super(RaySensor,self).Get_kwargs(ID_offset,object_ID_offset)

		kwargs['x'] = self.x+x_offset
		kwargs['y'] = self.y+y_offset
		kwargs['z'] = self.z+z_offset
		kwargs['r1'] = self.r1
		kwargs['r2'] = self.r2
		kwargs['r3'] = self.r3
		return kwargs

	def Send_To_Simulator(self,sim,ID_offset=0,object_ID_offset=0,x_offset=0,y_offset=0,z_offset=0):
		kwargs = self.Get_kwargs(ID_offset,object_ID_offset,x_offset,y_offset,z_offset)
		sim.Send_Ray_Sensor(**kwargs)


if __name__ == '__main__':
	from pyrosim import PYROSIM

	sim = PYROSIM(evalTime=200)
	sim.Start()
	# cyl = Cylinder(ID=0,z=1,r1=1,r2=0,r3=0)
	# joint = HingeJoint(ID=0,z=1,n1=0,n2=0,n3=1)
	# cyl.Send_To_Simulator(sim)
	# joint.Send_To_Simulator(sim)
	# sensor = PositionSensor(object_ID=0)
	# sensor.Send_To_Simulator(sim)
	# sim.Send_Sensor_Neuron(ID=0,sensorID=0,sensorValueIndex=2)
	# sim.Send_Motor_Neuron(ID=1)
	# sim.Send_Synapse(sourceNeuronIndex=0,targetNeuronIndex=1,weight=1.0)
	# sim.Start()
	# sim.Wait_To_Finish()
	# data = sim.Get_Results()
