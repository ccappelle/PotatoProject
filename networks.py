import numpy as np
import random
LO_INIT = -1.
HI_INIT = 1.

class Network(object):
	def __init__(self,num_sensors,num_hidden,num_motors,development_layers=1):
		self.num_sensors = num_sensors
		self.num_hidden = num_hidden
		self.num_motors = num_motors
		self.total_neurons = num_sensors+num_hidden+num_motors
		self.development_layers = development_layers
		self.adj_matrix = np.zeros((self.total_neurons,self.total_neurons,development_layers))

	def Send_To_Simulator(self,sim,sensor_indices=-1,motor_indices=-1,neuron_offset=0,sensor_offset=0,joint_offset=0,eval_time=500):
		if sensor_indices < 0:
			sensor_indices = range(self.num_sensors)

		if motor_indices < 0:
			motor_indices = range(self.num_motors)

		s_offset = neuron_offset
		for s_ID in range(self.num_sensors):
			sim.Send_Sensor_Neuron(ID=s_ID+s_offset, sensorID=sensor_offset+sensor_indices[s_ID])

		h_offset = s_offset+self.num_sensors
		for h_ID in range(self.num_hidden):
			sim.Send_Hidden_Neuron(ID=h_ID+h_offset)

		m_offset = h_offset + self.num_hidden
		for m_ID in range(self.num_motors):
			sim.Send_Motor_Neuron(ID=m_ID+m_offset, jointID=joint_offset+motor_indices[m_ID])

		for i in range(self.total_neurons):
			for j in range(self.total_neurons):
				if not(self.adj_matrix[i,j,0]==0):
					sourceNeuronIndex = neuron_offset+i
					targetNeuronIndex = neuron_offset+j


					start_weight = self.adj_matrix[i,j,0]
					end_weight = start_weight
					start_time = -1
					end_time = -1

					if self.development_layers==2:
						end_weight = self.adj_matrix[i,j,1]
						end_time = 1
					elif self.development_layers==3:
						end_weight = self.adj_matrix[i,j,1]
						end_time = self.adj_matrix[i,j,2]
					elif self.development_layers==4:
						end_weight = self.adj_matrix[i,j,1]
						start_time = self.adj_matrix[i,j,2]
						end_time = self.adj_matrix[i,j,3]

					start_time = int((start_time + 1.)*eval_time/2.)
					end_time = start_time + int((end_time +1.)*eval_time/2.)

					sim.Send_Changing_Synapse(sourceNeuronIndex=sourceNeuronIndex,targetNeuronIndex=targetNeuronIndex,
											start_weight=start_weight, end_weight=end_weight,
											start_time=start_time,end_time=end_time)
					print start_time, end_time, start_weight, end_weight
class LayeredNetwork(Network):

	def __init__(self,num_sensors=1,num_layers=1, hidden_per_layer=1, num_motors=1,back_connections=0,hidden_recurrence=0,motor_recurrence=0,development_layers=1):
		#Create an layered network with random weights returned as adjacency matrix
		#Dimensions and structure: num_sensors -> hidden_per_layer_{1} -> ... -> hidden_per_layer_{num_layers} -> num_motors
		#can add feed back connections between hidden neurons (back_connections=1)
		#can add recurrent connections (hidden_reccurent=1, motor_recurrent=1)
		super(LayeredNetwork,self).__init__(num_sensors=num_sensors,num_hidden=num_layers*hidden_per_layer,num_motors=num_motors,development_layers=development_layers)
		self.num_layers = num_layers
		self.hidden_per_layer = hidden_per_layer
		self.back_connections = back_connections
		self.hidden_recurrence = hidden_recurrence
		self.motor_recurrence = motor_recurrence

		neuronID = 0
		
		for from_layer in range(1+num_layers):
			if from_layer == 0: #If layer is sensor layer
				from_layer_size = num_sensors
			else: 
				from_layer_size = hidden_per_layer

			if from_layer == num_layers: #If layer is last hidden before motors
				to_layer_size = num_motors
			else:
				to_layer_size = hidden_per_layer

			from_neuron_start = neuronID
			to_neuron_start = neuronID + from_layer_size

			#Loop through each neuron pairing in the network and connect with weight equal to that location
			#in random matrix
			for from_neuronID in range(from_neuron_start,from_neuron_start+from_layer_size):
				for to_neuronID in range(to_neuron_start,to_neuron_start+to_layer_size):
					for d_index in range(self.development_layers):
						self.adj_matrix[from_neuronID,to_neuronID,d_index] = random.uniform(LO_INIT,HI_INIT)
						if back_connections == 1 and from_layer>0: #If back connections are on, connect back except to sensors
							self.adj_matrix[to_neuronID,from_neuronID,d_index] = random.uniform(LO_INIT,HI_INIT)
				neuronID+=1	

		if hidden_recurrence == 1: #If recurrent in hidden neurons add recurrent connections
			for neuron_ID in range(num_sensors,num_sensors+num_layers*hidden_per_layer):
				self.adj_matrix[neuron_ID,neuron_ID,d_index] = rand_mat[neuron_ID,neuron_ID,d_index]

		if motor_recurrence == 1: #If recurrent in motor neurons add recurrent connections
			for neuron_ID in range(num_sensors+num_layers*hidden_per_layer, total_neurons):
				self.adj_matrix[neuron_ID,neuron_ID,d_index] = rand_mat[neuron_ID,neuron_ID,d_index]

		self.total_weights = np.count_nonzero(self.adj_matrix)
		self.total_synapses = self.total_weights/self.development_layers

	def Get_Adj_Matrix(self):
		return self.adj_matrix

	def Mutate_One_Synapse(self,fromID,toID,development_layer=0,sigma=-1):
		if development_layer == 0 or development_layer == 1:
			if sigma<=0:
				sigma = self.adj_matrix[fromID,toID,development_layer]
				if sigma<0.05:
					sigma = 0.05

			if not(self.adj_matrix[fromID,toID,development_layer] == 0):
				self.adj_matrix[fromID,toID,development_layer] = self.adj_matrix[fromID,toID,development_layer] + random.gauss(0,sigma)

		else:
			if sigma<=0:
				sigma = .5

			if not(self.adj_matrix[fromID,toID,development_layer] == 0):
				new_value = self.adj_matrix[fromID,toID,development_layer] + random.gauss(0,sigma)
				if new_value>1:
					new_value == 1
				elif new_value<-1:
					new_value == -1

				self.adj_matrix[fromID,toID,development_layer] = new_value

	def Mutate_p(self,p=-1,sigma=-1):
		if p<0:
			p= 1./float(self.total_weights)

		weights = np.nonzero(self.adj_matrix)

		for i in range(self.total_weights):
			if random.random()<p:
				fromID,toID,development_layer = weights[0][i],weights[1][i],weights[2][i]
				self.Mutate_One_Synapse(fromID,toID,development_layer,sigma)

	def Mutate_n(self,n,sigma=-1):
		weights = np.nonzero(self.adj_matrix)
		#rands = np.random.permutation(self.total_weights)
		vals_to_choose = range(self.total_weights)

		for i in range(int(n)):
			rand = random.randrange(len(vals_to_choose))
			index = vals_to_choose.pop(rand)
			fromID, toID, development_layer = weights[0][index], weights[1][index], weights[2][index]
			self.Mutate_One_Synapse(fromID,toID,development_layer,sigma)

def Create_Biped_Network(num_layers=1,hidden_per_layer=8,back_connections=0,hidden_recurrence=0,motor_recurrence=0):
	BIPED_SENSORS = 2
	BIPED_MOTORS = 6
	return LayeredNetwork(num_sensors=QUAD_SENSORS,num_layers=num_layers,hidden_per_layer=hidden_per_layer,num_motors=QUAD_MOTORS,
							back_connections=back_connections,hidden_recurrence=hidden_recurrence,
							motor_recurrence=motor_recurrence)

if __name__ == "__main__":
	myNet = LayeredNetwork()
	#Create_Quad_Network()
	myNet.Mutate_p()
	


	