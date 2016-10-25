import numpy as np

class LayeredNetwork():

	def __init__(self,num_sensors=4,num_layers=1, num_hidden=8, num_motors=8,back_connections=0,hidden_recurrence=0,motor_recurrence=0):
		#Create an layered network with random weights returned as adjacency matrix
		#Dimensions and structure: num_sensors -> num_hidden_{1} -> ... -> num_hidden_{num_layers} -> num_motors
		#can add feed back connections between hidden neurons (back_connections=1)
		#can add recurrent connections (hidden_reccurent=1, motor_recurrent=1)
		neuronID = 0
		self.total_neurons = num_sensors + num_layers*num_hidden +num_motors
		self.adj_matrix = np.zeros((self.total_neurons,self.total_neurons))
		self.num_sensors = num_sensors
		self.num_layers = num_layers
		self.num_hidden = num_hidden
		self.num_motors = num_motors
		self.back_connections = back_connections
		self.hidden_recurrence = hidden_recurrence
		self.motor_recurrence = motor_recurrence

		#Random matrix where weights are drawn. Can be changed
		rand_mat = 2.*np.random.rand(self.total_neurons,self.total_neurons)-1.

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
					self.adj_matrix[from_neuronID,to_neuronID] = rand_mat[from_neuronID,to_neuronID]
					if back_connections == 1 and from_layer>0: #If back connections are on, connect back except to sensors
						self.adj_matrix[to_neuronID,from_neuronID] = rand_mat[to_neuronID,from_neuronID]
				neuronID+=1	

		if hidden_recurrence == 1: #If recurrent in hidden neurons add recurrent connections
			for neuron_ID in range(num_sensors,num_sensors+num_layers*num_hidden):
				self.adj_matrix[neuron_ID,neuron_ID] = rand_mat[neuron_ID,neuron_ID]

		if motor_recurrence == 1: #If recurrent in motor neurons add recurrent connections
			for neuron_ID in range(num_sensors+num_layers*num_hidden, total_neurons):
				self.adj_matrix[neuron_ID,neuron_ID] = rand_mat[neuron_ID,neuron_ID]


	def Get_Adj_Matrix():
		return self.adj_matrix



if __name__ == "__main__":
	myNet = LayeredNetwork()
	print isinstance(myNet,LayeredNetwork)
	print isinstance(myNet.adj_matrix,LayeredNetwork)
	print myNet.adj_matrix