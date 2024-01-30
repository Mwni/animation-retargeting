import json
from mathutils import Matrix, Quaternion
from .armature import Armature
from .mapping import Mappings
from .util import rot_mat


class Retargeter:
	def __init__(self, config_file):
		with open(config_file) as f:
			self.config = json.load(f)

		self.source = Armature(self.config['armatures']['source'])
		self.target = Armature(self.config['armatures']['target'])
		self.mappings = Mappings(self.config['mappings'], self.source)


	def __call__(self, bone_matrices):
		for bone_name, matrix in bone_matrices.items():
			self.source.pose_bones[bone_name].matrix_basis = matrix

		return {
			bone_name: self.calc_target_bone_mat(bone_name) 
			for bone_name in self.target.pose_bones.keys()
		}


	def calc_target_bone_mat(self, bone_name):
		mapping = self.mappings.get_for_target(bone_name)

		if not mapping:
			return Matrix.Identity(4)

		intermediate_bones = self.mappings.get_intermediate_bones(mapping)
		bone_mat = self.source.pose_bones[mapping.source].matrix_basis
		bone_loc = bone_mat.to_translation()
		bone_rot = bone_mat.to_quaternion()

		if len(intermediate_bones) > 0:
			src_bone = self.source.pose_bones[mapping.source]
			head_bone = intermediate_bones[0]
			tail_bone = intermediate_bones[-1]

			if tail_bone.parent:
				base_bone = tail_bone.parent
				base_rest = base_bone.bone.matrix_local.to_quaternion()
				base_pose = base_bone.matrix.to_quaternion()
			else:
				base_rest = Quaternion()
				base_pose = Quaternion()

			head_rest = head_bone.bone.matrix_local.to_quaternion()
			head_pose = head_bone.matrix.to_quaternion()

			based_pose = base_pose.inverted() @ head_pose
			based_rest = base_rest.inverted() @ head_rest

			based_delta = based_rest.inverted() @ based_pose
			mapped_delta = src_bone.bone.matrix.to_quaternion().inverted() @ based_delta @ src_bone.bone.matrix.to_quaternion()

			bone_rot @= mapped_delta

		src_data = self.source.data_bones[mapping.source]
		src_ref_mat = rot_mat(self.source.matrix_world) @ rot_mat(src_data.matrix_local)
		dest_ref_mat = rot_mat(self.target.matrix_world) @ rot_mat(mapping.rest)
		diff_mat = src_ref_mat.inverted() @ dest_ref_mat

		scale = self.source.matrix_world.to_scale()
		scale_mat = Matrix.Identity(4)
		scale_mat[0][0] = scale.x
		scale_mat[1][1] = scale.y
		scale_mat[2][2] = scale.z

		mat = Matrix.Translation(bone_loc) @ bone_rot.to_matrix().to_4x4()
		mat = scale_mat @ mat
		mat = diff_mat.inverted() @ mat @ diff_mat
		mat = mapping.offset @ mat
		mat = mat

		return mat