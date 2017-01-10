import random
import copy


HIDDEN = 0
MOTOR = 1
SENSOR = 2

class Synapse(object):
	def __init__(self,to_ID,from_ID,weight):
		self.to_ID = to_ID
		self.from_ID = from_ID
		self.weight = weight

	def Mutate(self,sigma=-1):
		if sigma<=0:
			sigma = self.weight
			if sigma<0.05:
				sigma = 0.05

		self.weight = self.weight + random.gauss(0,sigma)

	def Send_To_Simulator(self,sim,neuron_offset):
		sim.Send_Synapse(sourceNeuronIndex=self.from_ID+neuron_offset,
							targetNeuronIndex=self.to_ID+neuron_offset,
							weight = self.weight)

class Neuron(object):
	def __init__(self,my_ID,my_type,assoc_ID=-1):
		self.ID = my_ID
		self.type = my_type
		self.assoc_ID = assoc_ID

	def Send_To_Simulator(self,sim,neuron_offset=0,assoc_offset=0):
		if self.type == HIDDEN:
			sim.Send_Hidden_Neuron(ID=self.ID+neuron_offset)
		elif self.type == SENSOR:
			sim.Send_Sensor_Neuron(ID=self.ID+neuron_offset,sensorID=self.assoc_ID+assoc_offset)
		elif self.type == MOTOR:
			sim.Send_Motor_Neuron(ID=self.ID+neuron_offset,jointID=self.assoc_ID+assoc_offset)


class Network(object):
	def __init__(self):
		self.neurons = []
		self.synapses = []
		self.motor_neuron_indices = []
		self.sensor_neuron_indices = []
		self.hidden_neuron_incices = []
		self.total_neurons = 0

	@classmethod
	def Combine(cls,net1,net2):
		new_net = cls()

		for neuron in net1.neurons:
			new_net.Add_Neuron(neuron.type,neuron.assoc_ID)

		for neuron in net2.neurons:
			new_net.Add_Neuron(neuron.type,neuron.assoc_ID)

		for synapse in net1.synapses:
			new_net.Add_Synapse(synapse.to_ID,synapse.from_ID,synapse.weight)

		offset = len(net1.neurons)
		for synapse in net2.synapses:
			new_net.Add_Synapse(synapse.to_ID+offset,synapse.from_ID+offset,synapse.weight)

		return new_net

	def Add_Neuron(self,neuron_type,assoc_ID=0):
		ID = len(self.neurons)

		if neuron_type == MOTOR:
			self.neurons.append(Neuron(ID,MOTOR,assoc_ID))
			self.motor_neuron_indices.append(ID)
		elif neuron_type == SENSOR:
			self.neurons.append(Neuron(ID,SENSOR,assoc_ID))
			self.sensor_neuron_indices.append(ID)
		elif neuron_type == HIDDEN:
			self.neurons.append(Neuron(ID,HIDDEN))
			self.hidden_neuron_incices.append(ID)

		self.total_neurons += 1
		return ID

	def Add_Synapse(self,to_neuron,from_neuron,weight=False,hi=1,lo=-1):

		if not weight:
			weight = random.uniform(hi,lo)

		self.synapses.append( Synapse(to_neuron,from_neuron,weight))
	

	def Send_To_Simulator(self,sim,neuron_offset,joint_offset,sensor_offset):
		for neuron in self.neurons:
			if neuron.type == HIDDEN:
				neuron.Send_To_Simulator(sim,neuron_offset)
			elif neuron.type == MOTOR:
				neuron.Send_To_Simulator(sim,neuron_offset,joint_offset)
			elif neuron.type == SENSOR:
				neuron.Send_To_Simulator(sim,neuron_offset,sensor_offset)

		for synapse in self.synapses:
			synapse.Send_To_Simulator(sim,neuron_offset)

		return len(self.neurons)

	def Mutate_p(self,p,sigma=-1):
		for synapse in self.synapses:
			if float(p) >random.random():
				synapse.Mutate(sigma)


class Layered_Network(Network):
	def __init__(self,sensor_ids,motor_ids,hidden_layers,back_connections=False,hidden_recurrence=False,motor_recurrence=False):
		super(Layered_Network,self).__init__()

		self.num_sensors = len(sensor_ids)
		self.num_motors = len(motor_ids)
		self.num_hidden = sum(hidden_layers)

		self.num_layers = len(hidden_layers)+2

		self.layers = [0]*self.num_layers

		for i in range(self.num_layers):
			if i == 0:
				num_neurons = self.num_sensors
				neuron_type = SENSOR
			elif i == self.num_layers-1:
				num_neurons = self.num_motors
				neuron_type = MOTOR
			else:
				num_neurons = hidden_layers[i-1]
				neuron_type = HIDDEN

			self.layers[i] = []
			for j in range(num_neurons):
				if neuron_type ==SENSOR:
					self.Add_Neuron(i,SENSOR,sensor_ids[j])
				elif neuron_type == MOTOR:
					self.Add_Neuron(i,MOTOR,motor_ids[j])
				else:
					self.Add_Neuron(i,HIDDEN)

		for i in range(self.num_layers-1):
			up_layer = self.layers[i]
			down_layer = self.layers[i+1]

			for up_neuron_ID in up_layer:
				for down_neuron_ID in down_layer:
					self.Add_Synapse(down_neuron_ID,up_neuron_ID)
					if not(i == 0): 
						if back_connections:
							self.Add_Synapse(up_neuron_ID,down_neuron_ID)

						if hidden_recurrence:
							self.Add_Synapse(up_neuron_ID,up_neuron_ID)


		for motor_id in self.layers[-1]:
			if back_connections:
				for hidden_id in self.layers[-2]:
					self.Add_Synapse(hidden_id,motor_id)

			if motor_recurrence:
				self.Add_Synapse(motor_id,motor_id)


	def Add_Neuron(self,layer,neuron_type,assoc_ID=0):
		ID = super(Layered_Network,self).Add_Neuron(neuron_type,assoc_ID)
		self.neurons[ID].layer = layer
		self.layers[layer].append(ID)

		return ID

if __name__ == "__main__":
	net1 = Layered_Network([0,1],[0,1,2],[1])
	# net1 = Layered_Network([0],[0],[1])
	# net2 = Layered_Network([1],[1],[1])
	# new_net = Network.Combine(net1,net2)
	# for synapse in new_net.synapses:
	# 	print synapse.from_ID,synapse.to_ID,synapse.weight

	# prob = 1./float(len(new_net.synapses))
	# print prob
	# new_net.Mutate_p(prob)
	# print '----'
	# for synapse in new_net.synapses:
	# 	print synapse.from_ID,synapse.to_ID,synapse.weight
