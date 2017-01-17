import simObjects
import math
import numpy as np
class Environment(object):
	def __init__(self, init_objects = []):
		self.env_objects = []
		for env_object in init_objects:
			self.env_objects.append(env_object)

	def Add_Env_Object(self,env_object):
		self.env_objects.append(env_object)

	def Add_Env_Objects(self,env_objects):
		for env_object in env_objects:
			self.env_objects.append(env_object)

	def Send_To_Simulator(self, sim, ID_offset):
		for env_object in self.env_objects:
			env_object.Send_To_Simulator(sim,ID_offset=ID_offset)
			ID_offset += 1

		return ID_offset

class Cluster(object):
	def __init__(self, num_in,line_length,center_position,angle,color=[1,1,1]):
		
		self.diameter = line_length/float(num_in)
		direction_vector = np.array([math.cos(angle),math.sin(angle)])
		center_position = np.array(center_position)

		self.line_start = center_position[:2]-direction_vector*line_length/2.0
		self.line_end = center_position[:2]+direction_vector*line_length/2.0

		self.num_in = num_in
		self.line_length = line_length
		self.center_position = center_position
		self.angle = angle
		self.cluster_centers = np.zeros((num_in,2))		
		self.objects_in_cluster = []
		self.color = color

		for i in range(self.num_in):			 
			self.cluster_centers[i,:] = self.line_start+(self.diameter/2.0)*direction_vector + i*(self.diameter)*direction_vector
			
			cyl = simObjects.Cylinder(x=self.cluster_centers[i,0],y=self.cluster_centers[i,1],
												z=center_position[2], collision=False,
												r1=0,r2=0,r3=1,length=1.0,radius=self.diameter/2.0+.05,
												r=self.color[0],g=self.color[1],b=self.color[2])
			self.objects_in_cluster.append(cyl)

	
	def Plot_Cluster(self):
		plt.plot([self.line_start[0],self.line_end[0]],[self.line_start[1],self.line_end[1]])
		plt.plot(self.cluster_centers[:,0],self.cluster_centers[:,1],'ro')

	def Get_Num_In_Cluster(self):
		return self.num_in

class Cluster_Env(Environment):
 	"""docstring for Tree_E"""
 	ODD_COLOR = [1,0,1]
 	EVEN_COLOR = [0,1,1]

 	def __init__(self, num_per_cluster, center_positions, cluster_angles,line_length,colors):
 		super(Cluster_Env,self).__init__()
 		self.num_clusters = len(num_per_cluster)
 		self.clusters = []
 		for i in range(self.num_clusters):
 			new_cluster = Cluster(num_per_cluster[i],line_length[i],center_positions[i],cluster_angles[i],colors[i])
 			self.clusters.append(new_cluster)
 			self.Add_Env_Objects(new_cluster.objects_in_cluster)

 	def Plot_Env(self):
 		for cluster in self.clusters:
 			cluster.Plot_Cluster()
 	def Get_Odd_And_Even(self):
 		odd = 0
 		even = 0

 		for cluster in self.clusters:
 			num_in = cluster.Get_Num_In_Cluster()
 			if num_in%2==0:
 				even += 1
 			else:
 				odd += 1

 		return odd, even

	@classmethod
	def Bi_Sym(cls, num_in_left,num_in_right, distance, line_length,origin=(0.,1.,0.5)):
		l_direction = np.array([-1,1,0])
		r_direction = np.array([1,1,0])
		origin = np.array(origin)
		l_direction = l_direction/np.linalg.norm(l_direction)
		r_direction = r_direction/np.linalg.norm(r_direction)
		center_positions = []
		center_positions.append(l_direction*distance+origin)
		center_positions.append(r_direction*distance+origin)
		cluster_angles = [math.pi/4,-math.pi/4]
		if num_in_left %2==0:
			l_color = cls.EVEN_COLOR
		else:
			l_color = cls.ODD_COLOR

		if num_in_right%2==0:
			r_color = cls.EVEN_COLOR
		else:
			r_color = cls.ODD_COLOR

		env = cls([num_in_left,num_in_right], center_positions, cluster_angles,[line_length,line_length],[l_color,r_color])

		return env

if __name__=="__main__":
	import matplotlib.pyplot as plt
 	from pyrosim import PYROSIM

 	sim = PYROSIM(playPaused=False,playBlind=False,evalTime = 200)
 	#env = Cluster_Env.Bi_Sym(3,2,4,2)
 	#env = Environment()
 	env.Send_To_Simulator(sim,0)
 	sim.Start()
 	