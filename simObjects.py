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
	def __init__(self,x=0, y=0, z=0, r1=0, r2=0, r3=1, length=1.0, radius=0.1, r=1, g=1, b=1):
		super(Cylinder,self).__init__(x=x,y=y,z=z,r=r,g=g,b=b)
		self.r1 = r1
		self.r2 = r2
		self.r3 = r3
		self.length = length
		self.radius = radius

	def Send_To_Simulator(self,sim,x_offset=0,y_offset=0,z_offset=0,ID_offset=0):
		kwargs = self.Get_kwargs(x_offset,y_offset,z_offset,ID_Offset)
		p
		sim.Send_Cylinder(kwargs)

	def Get_kwargs(self,x_offset=0,y_offset=0,z_offset=0,ID_offset=0):
		kwargs = super(Cylinder,self).Get_kwargs(x_offset,y_offset,z_offset,ID_Offset)
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
	def __init__(self,ID=0,firstObjectID=0,secondObjectID=-1,x=0,y=0,z=0,n1=0,n2=0,n3=0,lo=-math.pi/4.0,hi=math.pi/4.0,speed=1.0):
		super(HingeJoint,self).__init__(ID=ID,firstObjectID=firstObjectID,secondObjectID=secondObjectID,
										x=x,y=y,z=z)
		self.n1 = n1
		self.n2 = n2
		self.n3 = n3
		self.lo = lo
		self.hi = hi

	def Send_To_Simulator(self,sim,x_offset=0,y_offset=0,z_offset=0,object_ID_offset=0,ID_offset=0):
		kwargs = self.Get_kwargs(x_offset,y_offset,z_offset,ID_Offset,object_ID_offset)
		sim.Send_Joint(self,ID=self.ID+ID_offset,
						firstObjectID=self.firstObjectID+object_ID_offset,
						secondObjectID=secondObjectID, x=self.x+x_offset,
						y=self.y+y_offset, z=self.z+z_offset,n1=self.n1,
						n2=self.n2,n3=self.n3,lo=self.lo,hi=self.hi)

	def Get_kwargs(self,x_offset=0,y_offset=0,z_offset=0,ID_Offset=0,object_ID_offset=0):
		kwargs = super(HingeJoint,self).Get_kwargs(x_offset,y_offset,z_offset,ID_Offset,object_ID_offset)
		if self.secondObjectID < 0:
			kwargs['secondObjectID'] = -1
		kwargs['lo'] = self.lo
		kwargs['hi'] = self.hi
		kwargs['n1'] = self.n1
		kwargs['n2'] = self.n2
		kwargs['n3'] = self.n3

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
	def Send_To_Simulator(self,sim,ID_Offset=0,object_ID_offset=0):
		kwargs = self.Get_kwargs(ID_offset,object_ID_offset)
		sim.Send_Touch_Sensor(**kwargs)


