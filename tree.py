import math
import copy
import numpy as np

XY_PLANE = 0
XZ_PLANE = 1
YZ_PLANE = 2

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
		pass

	def Add_Subtree(self, subtree):
		self.num_children += 1
		self.children.append(subtree)
		subtree.parent_ID = self.node_ID

		self.is_leaf = False
		self.leaf_list=[]
		for child in self.children:
			self.leaf_list.append(child.leaf_list)

	def Translate_Base_To_Pos(self,new_pos):
		translation = [0]*len(new_pos)
		for i in range(len(new_pos)):
			translation[i] = new_pos[i] - self.base_position[i]

		self.Translate_By_Vec(translation)

	def Translate_By_Vec(self,translation):
		for i in range(len(translation)):
			self.base_position[i] += translation[i]
			self.tip_position[i] += translation[i]

		for child in self.children:
			child.Translate_By_Vec(translation)
	def Rotate_About_Origin(self, angle, rotation_plane=XY_PLANE):
		if rotation_plane == XY_PLANE:
			rot_mat = [[math.cos(angle), -math.sin(angle), 0],
					[math.sin(angle), math.cos(angle), 0],
					[0,0,1]]
		elif rotation_plane == XZ_PLANE:
			rot_mat = [[math.cos(angle), 0, -math.sin(angle)],
						[0, 1, 0],
						[math.sin(angle), 0, math.cos(angle)]]
		elif rotation_plane == YZ_PLANE:
			rot_mat = [[1, 0, 0],
						[0, math.cos(angle), math.sin(angle)],
						[0, -math.sin(angle), math.cos(angle)]]

		new_tip = [0]*len(self.tip_position)
		new_base = [0]*len(self.base_position)

		for i in range(len(self.base_position)):
			for j in range(len(self.base_position)):
				new_tip[i] += self.tip_position[j]*rot_mat[i][j]
				new_base[i] += self.base_position[j]*rot_mat[i][j]

		self.base_position = new_base
		self.tip_position = new_tip

		for child in self.children:
			child.Rotate_About_Origin(angle, rotation_plane = rotation_plane)

	def Rotate_About_Pos(self, angle, rotation_position, rotation_plane=XY_PLANE):
		neg_translation = [0]*len(rotation_position)
		pos_translation = [0]*len(rotation_position)
		for i in range(len(rotation_position)):
			neg_translation[i] = -rotation_position[i]
			pos_translation[i] = rotation_position[i]
		self.Translate_By_Vec(neg_translation)
		self.Rotate_About_Origin(angle, rotation_plane)
		self.Translate_By_Vec(pos_translation)


	def Rotate_About_Base(self, angle, rotation_plane=XY_PLANE):
		pos = self.base_position
		self.Rotate_About_Pos(angle,pos)

	def Rotate_About_Tip(self, angle, rotation_plane=XY_PLANE):
		pos = self.tip_position
		self.Rotate_About_Pos(angle,pos)

	def Rotate_About_Center(self, angle, rotation_plane=XY_PLANE):
		center = [0]*len(self.base_position)
		for i in range(len(center)):
			center[i] = (base_position[i]+tip_position[i])/2.0
		pos = center
		self.Rotate_About_Pos(angle,pos)

	def Recalc(self, start_ID=0):
		self.node_ID = start_ID
		last_ID = start_ID

		if self.is_leaf == True:
			self.leaf_list = [self.node_ID]
		else:
			self.leaf_list = []
			for child in self.children:
				last_ID, leaf_list = child.Recalc(last_ID+1)
				self.leaf_list.append(leaf_list)

		self.last_ID = last_ID
		

		return self.last_ID, self.leaf_list

	def Scale(self,scale_factor):
		normalized_orientation = [0]*3
		new_branch_length = scale_factor*self.branch_length

		for i in range(3):
			normalized_orientation[i] = (self.tip_position[i]-self.base_position[i])/self.branch_length
		
		for i in range(3):
			self.tip_position[i] = self.base_position[i]+ normalized_orientation[i]*new_branch_length	 

		self.Recalc_Branch_Length()

		for child in self.children:
			child.Translate_Base_To_Pos(self.tip_position)

	def Scale_Whole_Tree(self,scale_factor):
		self.Scale(scale_factor)
		for child in self.children:
			child.Scale_Whole_Tree(scale_factor)

	def Recalc_Branch_Length(self):
		temp_sum = 0.0
		for i in range(3):
			temp_sum += math.pow((self.tip_position[i]-self.base_position[i]),2.0)
		self.branch_length = math.sqrt(temp_sum)
		return self.branch_length

class Sym_Tree(Base_Tree):
	def __init__(self,num_children=2,current_depth=0,max_depth=1,base_position=[0,0,0],
					branch_length=1,global_angle=0,lo_angle=-math.pi/4,hi_angle= math.pi/4,node_ID=0,parent_ID=-1):

		self.node_ID = node_ID
		self.parent_ID = parent_ID
		self.highest_child_ID = node_ID
		self.branch_length = float(branch_length)

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
				child = Sym_Tree(num_children=self.lineage, current_depth=self.depth+1,
					max_depth=self.max_depth, base_position=[self.tip_position[0],self.tip_position[1],self.tip_position[2]], 
					branch_length=self.branch_length,
					global_angle=child_angle,lo_angle=lo_angle/2.0,hi_angle=hi_angle/2.0, 
					node_ID=child_ID,parent_ID=self.node_ID)
				self.num_leaves += child.num_leaves
				self.highest_child_ID = child.highest_child_ID
				self.num_nodes += child.num_nodes
				
				for leaf_ID in child.leaf_list:
					self.leaf_list.append(leaf_ID)
				self.children.append(child)	


	def Scale_Node(self,target_node_ID, scale_factor):
		found = False
		if self.node_ID == target_node_ID:
			self.Scale(scale_factor)
			return True
		else:
			for child in self.children:
				if child.highest_child_ID >= target_node_ID and child.node_ID<=target_node_ID:
					found = child.Scale_Node(target_node_ID, scale_factor)
				if found:
					return True
		return found

	def Rotate_Node(self,target_node_ID,angle, rotation_plane=XY_PLANE):
		found = False
		if self.node_ID == target_node_ID:
			self.Rotate_About_Base(angle,rotation_plane)
			return True
		else:
			for child in self.children:
				if child.highest_child_ID >= target_node_ID and child.node_ID<=target_node_ID:
					found = child.Rotate_Node(target_node_ID, angle,rotation_plane)
				if found:
					return True
		return found
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




