from pyrosim import PYROSIM
import numpy as np
import math

def Create_Layered_Network(num_sensors=4,num_layers=1, num_hidden=8, num_motors=8,back_connections=0,hidden_recurrence=0,motor_recurrence=0):
	#Create an layered network with random weights returned as adjacency matrix
	#Dimensions and structure: num_sensors -> num_hidden_{1} -> ... -> num_hidden_{num_layers} -> num_motors
	#can add feed back connections between hidden neurons (back_connections=1)
	#can add recurrent connections (hidden_reccurent=1, motor_recurrent=1)
	neuronID = 0
	total_neurons = num_sensors+num_layers*num_hidden+num_motors
	adj_matrix = np.zeros((total_neurons,total_neurons))

	#Random matrix where weights are drawn. Can be changed
	rand_mat = 2.*np.random.rand(total_neurons,total_neurons)-1.

	for from_layer in range(1+num_layers):
		if from_layer == 0: #If layer is sensor layer
			from_layer_size = num_sensors
		else: 
			from_layer_size = num_hidden

		if from_layer == num_layers: #If layer is last hidden before motors
			to_layer_size = num_motors
		else:
			to_layer_size = num_hidden

		from_neuron_start = neuronID
		to_neuron_start = neuronID + from_layer_size

		#Loop through each neuron pairing in the network and connect with weight equal to that location
		#in random matrix
		for from_neuronID in range(from_neuron_start,from_neuron_start+from_layer_size):
			for to_neuronID in range(to_neuron_start,to_neuron_start+to_layer_size):
				adj_matrix[from_neuronID,to_neuronID] = rand_mat[from_neuronID,to_neuronID]
				if back_connections == 1 and from_layer>0: #If back connections are on, connect back except to sensors
					adj_matrix[to_neuronID,from_neuronID] = rand_mat[to_neuronID,from_neuronID]
			neuronID+=1	

	if hidden_recurrence == 1: #If recurrent in hidden neurons add recurrent connections
		for neuron_ID in range(num_sensors,num_sensors+num_layers*num_hidden):
			adj_matrix[neuron_ID,neuron_ID] = rand_mat[neuron_ID,neuron_ID]

	if motor_recurrence == 1: #If recurrent in motor neurons add recurrent connections
		for neuron_ID in range(num_sensors+num_layers*num_hidden, total_neurons):
			adj_matrix[neuron_ID,neuron_ID] = rand_mat[neuron_ID,neuron_ID]

	return adj_matrix



def Send_Quadruped_Body_And_Brain(sim,x=0,y=0,z=0.3,body_length=0.5,body_height=0.1,objID=0,jointID=0,sensorID=0,neuronID=0,
								num_sensors=4,num_layers=1, num_hidden=8, num_motors=8,back_connections=0,hidden_recurrence=0,motor_recurrence=0,color=[0,0,0],network=-1):
	#Create a quadruped in sim simulation with designated parameters

	#Create the body
	new_objID,new_jointID,new_sensorID = Send_Quadruped_Body(sim, x=x,y=y,z=z,body_length=body_length,body_height=body_height,objID=objID,jointID=jointID,sensorID=sensorID,color=color)
	
	#Create the brain
	new_neuronID = Send_Quadruped_Brain(sim, num_sensors=num_sensors,num_layers=num_layers,num_hidden=num_hidden,num_motors=num_motors, 
							back_connections=back_connections,hidden_recurrence=hidden_recurrence,motor_recurrence=motor_recurrence,
							objID=objID,jointID=jointID,sensorID=sensorID,neuronID=neuronID,network=network)

	return new_objID,new_jointID,new_sensorID,new_neuronID #Returns the last index of ID vals. Useful for making multiple


def Send_Quadruped_Brain(sim,num_sensors=4,num_layers=1, num_hidden=8, num_motors=8,back_connections=0,hidden_recurrence=0,motor_recurrence=0,objID=0,jointID=0,sensorID=0,neuronID=0,network=-1):
	#Sends a neural net to the simulator

	if network == -1: #If network does not exist create random one
		network = Create_Layered_Network(num_sensors=num_sensors,num_layers=num_layers,num_hidden=num_hidden,num_motors=num_motors,back_connections=back_connections,
										hidden_recurrence=hidden_recurrence, motor_recurrence=motor_recurrence)

	total_neurons = num_sensors + num_layers*num_hidden + num_motors

	sensor_neuron_start = neuronID
	for sensor_index in range(num_sensors): #Send sensor neurons to sim
		sim.Send_Sensor_Neuron(ID=sensor_neuron_start+sensor_index,sensorID=sensor_index+sensorID)

	hidden_neuron_start = sensor_neuron_start + num_sensors
	for hidden_index in range(num_layers*num_hidden): #Send hidden neurons to sim
		sim.Send_Hidden_Neuron(ID=hidden_neuron_start+hidden_index)

	motor_neuron_start = hidden_neuron_start + num_hidden*num_layers
	for motor_index in range(num_motors): #Send motor neurons to sim
		sim.Send_Motor_Neuron(ID=motor_neuron_start+motor_index, jointID= jointID+motor_index)

	for i in range(total_neurons):
		for j in range(total_neurons):
			if not(network[i,j]==0): #Connect neurons with synapses from network adj matrix
				sim.Send_Synapse( neuronID+i,neuronID+j,network[i,j])

	new_neuronID = neuronID + total_neurons

	return new_neuronID


def Send_Quadruped_Body(sim, x=0,y=0,z=0.3,body_length=0.5,body_height=0.1,objID=0,jointID=0,sensorID=0,color=[0,0,0]):
	#Send the body of the quadruped with designated parameters

	pos = (x,y,z)
	z_incr = 0.05
	bodyID = objID
	objID += 1
	(r,g,b) = color

	#Body 
	sim.Send_Box(ID=bodyID, x=x,y=y,z=z+z_incr,length=body_length,width=body_length,height=body_height,r=r,g=g,b=b)

	#Auto asign legs based on how high the body is set to be
	leg_length = z
	radius = .5*body_height

	delta = 0.
	for i in range(4):
		x = math.cos(delta)
		y = math.sin(delta)
		delta += math.pi/2.0
		bl_length1 = (body_length+leg_length)/2.
		bl_length2 = body_length/2.+leg_length

		thighID = objID
		objID += 1
		calfID = objID
		objID += 1
		#Thigh
		sim.Send_Cylinder(ID=thighID, x=x*bl_length1+pos[0],y=y*bl_length1+pos[1],z=z+z_incr,r1=x,r2=y,r3=0,length=leg_length,radius=radius,r=r,g=g,b=b)
		
		#Calf
		sim.Send_Cylinder(ID=calfID, x=x*bl_length2+pos[0],y=y*bl_length2+pos[1],z=z/2.+z_incr,r1=0,r2=0,r3=1, length=z,radius=radius,r=r,g=g,b=b)

		#Hip joint
		sim.Send_Joint(ID=jointID, firstObjectID=bodyID, secondObjectID=thighID, x=x*body_length/2.+pos[0],y=y*body_length/2.+pos[1],z=z+z_incr,n1=y,n2=x,n3=0)
		jointID+=1

		#Knee Joint
		sim.Send_Joint(ID=jointID, firstObjectID=thighID, secondObjectID=calfID, x=x*bl_length2+pos[0],y=y*bl_length2+pos[1],z=z+z_incr,n1=y,n2=x,n3=0)
		jointID+=1

		#Sensor on feet
		sim.Send_Touch_Sensor(ID=sensorID, objectIndex=calfID)
		sensorID += 1
	
	#Send a position sensor attached to the body
	sim.Send_Position_Sensor(ID=sensorID,objectIndex=bodyID)
	print sensorID
	sensorID +=1

	return objID, jointID, sensorID


if __name__ == '__main__':
	T = 1000
	sim = PYROSIM(playPaused = False,playBlind=False, evalTime = T)
	objID = 0
	jointID = 0
	sensorID = 0
	neuronID = 0
	pos_sensor_list = []
	N = 4
	for i in range(N): #Create N potatoes, each with a different random network
		color = np.random.rand(3)
		objID,jointID,sensorID, neuronID = Send_Quadruped_Body_And_Brain(sim, x=i*1.5-N/2.,objID=objID,jointID=jointID,sensorID=sensorID,neuronID=neuronID,color=color)
		pos_sensor_list.append(sensorID-1)

	sim.Start()
	sim.Wait_To_Finish()
	print pos_sensor_list
	for i in range(N):
		for j in range(3):
			print sim.Get_Sensor_Data(pos_sensor_list[i],j,T-1)
		print '--------'
	#sim.Get_Sensor_Data(pos_sensor_list[0],0,0)
	#print Create_Layered_Network(back_connections=1,hidden_recurrence=0,motor_recurrence=0)
# sim.Collect_Sensor_Data()
