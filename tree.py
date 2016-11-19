import math
import copy
class Base_Tree(object):
	def __init__(self, base_position, tip_position, current_depth=0, node_ID=0,parent_ID=-1):
		self.node_ID = node_ID
		self.parent_ID = parent_ID
		self.depth = depth

		self.base_position = base_position
		self.tip_position = tip_position

		self.num_children = 0
		self.children = []

		self.is_leaf = True
		self.num_leaves = 1
		self.leaf_list = [self.node_ID]

	def Add_Subtree(self, subtree):
		self.num_children += 1
		self.children.append(subtree)
		subtree.parent_ID = self.node_ID

		self.leaf_list=[]
		for child in self.children:
			self.leaf_list.append(child.leaf_list)

	def Translate_Base_To_Pos(self,new_pos):
		translation = [0]*len(new_pos)
		for i in range(len(new_pos)):
			translation[i] = new_pos[i] - self.base_position[i]

		self.Translate_Base_By_Vec(translation)

	def Translate_By_Vec(self,translation):
		for i in range(len(self.translation)):
			base_position[i] += translation[i]
			tip_position[i] += translation[i]

		for child in self.children:
			child.Translate_By_Vec(translation)

	def Rotate_About_Origin(self,angle):
		for i in range(len(self.base_position)):
			self.base_position[i] = pass
			self.tip_position[i] = pass

		for child in self.children:
			child.Rotate_About_Origin(angle)

	def Rotate_About_Pos(self, angle, rotation_position):
		neg_translation = [0]*len(rotation_position)
		pos_translation = [0]*len(rotation_position)
		for i in range(len(rotation_position)):
			neg_translation[i] = -rotation_position[i]
			pos_translation[i] = rotation_position[i]
		self.Translate_By_Vec(neg_translation)
		self.Rotate_About_Origin(angle)
		self.Translate_By_Vec(pos_translation)


	def Rotate_About_Base(self, angle):
		pos = self.base_position
		self.Rotate_About_Pos(self,angle,pos)

	def Rotate_About_Tip(self, angle):
		pos = self.tip_position
		self.Rotate_About_Pos(self,angle,pos)

	def Rotate_About_Center(self, angle):
		center = [0]*len(self.base_position)
		for i in range(len(center)):
			center[i] = (base_position[i]+tip_position[i])/2.0
		pos = center
		self.Rotate_About_Pos(self,angle,pos)

class Tree(object):
	def __init__(self,num_children=2,current_depth=0,max_depth=1,base_position=[0,0,0],
					branch_length=1,global_angle=0,lo_angle=-math.pi/4,hi_angle= math.pi/4,node_ID=0,parent_ID=-1):

		self.node_ID = node_ID
		self.parent_ID = parent_ID
		self.highest_child_ID = node_ID
		self.branch_length = branch_length

		self.base_position = base_position
		self.tip_position = [0]*3
		self.tip_position[0] = base_position[0] +  self.branch_length*math.sin(global_angle)

		self.tip_position[1] = base_position[1] +  self.branch_length*math.cos(global_angle)
		self.tip_position[2] = base_position[2]


		self.depth = current_depth
		self.max_depth = max_depth

		self.angle = global_angle
		self.lo_angle = lo_angle
		self.hi_angle = hi_angle
		
		self.is_leaf = False
		if self.depth == max_depth:
			self.is_leaf = True
			self.children = []
			self.num_children = 0
			self.num_leaves = 1
			self.num_nodes = 1
			self.leaf_list = [self.node_ID]
		else:
			self.leaf_list = []
			self.num_leaves = 0
			self.num_nodes = 1
			if isinstance(num_children,int):
				self.num_children = num_children
				self.lineage = num_children
			else:
				self.num_children = num_children[0]
				self.lineage = [0]*(len(num_children)-1)
				for i in range(len(self.lineage)):
					self.lineage[i] = num_children[i+1]

			self.children = []
			angle_incr = (hi_angle- lo_angle)/ float(self.num_children-1)

			for nc in range(self.num_children):
				child_angle = self.angle + lo_angle + nc*angle_incr
				child_ID = self.highest_child_ID + 1
				child = Tree(num_children=self.lineage, current_depth=self.depth+1,
					max_depth=self.max_depth, base_position=self.tip_position, branch_length=self.branch_length,
					global_angle=child_angle,lo_angle=lo_angle/2.0,hi_angle=hi_angle/2.0, 
					node_ID=child_ID,parent_ID=self.node_ID)
				self.num_leaves += child.num_leaves
				self.highest_child_ID = child.highest_child_ID
				self.num_nodes += child.num_nodes
				
				for leaf_ID in child.leaf_list:
					self.leaf_list.append(leaf_ID)
				self.children.append(child)
				
				


	def Plot_Tree(self,ax):
		plt.plot([self.tip_position[1],self.base_position[1]],[self.tip_position[0],self.base_position[0]])
		center = self.Get_Center()
		ax.text(center[1],center[0],str(self.node_ID))
		for c in self.children:
			c.Plot_Tree(ax)

	def Get_Center(self):
		center = [0]*3
		for i in range(3):
			center[i] = (self.base_position[i]+self.tip_position[i])/2.0
		return center

	def Get_Orientation(self):
		orientation = [0]*3
		for i in range(3):
			orientation[i] = self.tip_position[i]-self.base_position[i]
		return orientation

if __name__ == "__main__":
	import matplotlib.pyplot as plt
	num_children = 4
	max_depth = 2
	branch_length = .75


	t = Tree(num_children=num_children,current_depth=0,max_depth=max_depth, 
		branch_length=branch_length,
		base_position=[0,0,0.5],lo_angle=-math.pi/4.,hi_angle=math.pi/4.,global_angle=math.pi/2.0,node_ID=0)

	print t.num_leaves,t.num_nodes,t.leaf_list
	fig = plt.figure()
	ax = fig.add_subplot(111)
	t.Plot_Tree(ax)
	plt.show()
