from pyrosim import PYROSIM
import math
ARM_LENGTH = 0.5

ARM_RADIUS = ARM_LENGTH / 10.0

sim = PYROSIM(playPaused = False , evalTime = 250)

z = 0.5

x_1 = 0
y_1 = ARM_LENGTH/2.0
z_1 = z
x_2 = ARM_LENGTH*math.cos(math.pi/4.)/2.0
y_2 = ARM_LENGTH*math.sin(math.pi/4.)/2.0+ARM_LENGTH
print x_2, y_2
x_3 = -x_2
y_3 = y_2

sim.Send_Cylinder(ID = 0 , x=x_1, y=y_1, z=z, r1=0, r2=1, r3=0, length=ARM_LENGTH, radius=ARM_RADIUS)
sim.Send_Cylinder(ID = 1 , x=x_2, y=y_2, z=z, r1=1, r2=1, r3=0, length=ARM_LENGTH, radius=ARM_RADIUS)
sim.Send_Cylinder(ID = 2 , x=x_3, y=y_3, z=z, r1=-1,r2=1,r3=0, length=ARM_LENGTH,radius =ARM_RADIUS)

sim.Send_Joint(ID = 0, firstObjectID=0, x=0, y=0, z=z, n1=0, n2=0, n3=1, lo=-3.14159/4.0, hi=+3.14159/4.0)
sim.Send_Joint(ID = 1, firstObjectID=0, secondObjectID=1,x=0, y=1, z=z, n1=0, n2=0, n3=1, lo=-3.14159/4.0, hi=+3.14159/4.0)
sim.Send_Joint(ID = 2, firstObjectID=0, secondObjectID=2,x=0, y=1, z=z, n1=0, n2=0, n3=1, lo=-3.14159/4.0, hi=+3.14159/4.0)

sim.Send_Touch_Sensor(ID = 0 , objectIndex = 0)

sim.Send_Touch_Sensor(ID = 1 , objectIndex = 1)

sim.Send_Sensor_Neuron(ID=0, sensorID=0 )

sim.Send_Sensor_Neuron(ID=1, sensorID=1 )

sim.Send_Motor_Neuron(ID = 2 , jointID = 0 )
sim.Send_Motor_Neuron(ID = 3 , jointID = 1 )
sim.Send_Motor_Neuron(ID = 4 , jointID = 2 )
sim.Send_Bias_Neuron(ID= 5 )
sim.Send_Synapse(sourceNeuronIndex = 0 , targetNeuronIndex = 2 , weight = 1.0 )
sim.Send_Synapse(sourceNeuronIndex = 5 , targetNeuronIndex = 2 , weight = -1.0 )

sim.Start()

# sim.Collect_Sensor_Data()