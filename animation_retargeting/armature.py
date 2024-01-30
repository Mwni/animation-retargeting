from mathutils import Matrix
from .util import list_to_matrix


class Armature:
	def __init__(self, config):
		self.matrix_world = list_to_matrix(config['matrix_world'])
		self.data_bones = {name: DataBone(name, bone) for name, bone in config['bones'].items()}
		self.pose_bones = {name: PoseBone(name, data_bone) for name, data_bone in self.data_bones.items()}

		for name, bone in config['bones'].items():
			if bone['parent']:
				self.data_bones[name].parent = self.data_bones[bone['parent']]
				self.pose_bones[name].parent = self.pose_bones[bone['parent']]


class DataBone:
	def __init__(self, name, config):
		self.name = name
		self.parent = None
		self.matrix = list_to_matrix(config['matrix'])
		self.matrix_local = list_to_matrix(config['matrix_local'])

class PoseBone:
	def __init__(self, name, data_bone):
		self.name = name
		self.parent = None
		self.bone = data_bone
		self.matrix_basis = Matrix.Identity(4)

	@property
	def matrix(self):
		matrix = self.bone.matrix.to_4x4() @ self.matrix_basis

		if self.parent:
			matrix = self.parent.matrix @ matrix

		return matrix