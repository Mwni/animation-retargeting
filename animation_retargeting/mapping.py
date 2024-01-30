from .util import list_to_matrix


class Mappings:
	def __init__(self, config, source_armature):
		self.source_armature = source_armature
		self.mappings = [Mapping(**m) for m in config]

	def get_for_target(self, name):
		return next((m for m in self.mappings if m.target == name), None)
	
	def get_intermediate_bones(self, mapping):
		bone = self.source_armature.pose_bones[mapping.source]
		intermediate_bones = []

		while bone.parent and not any(m.source == bone.parent.name for m in self.mappings):
			intermediate_bones.append(bone.parent)
			bone = bone.parent

		return intermediate_bones


class Mapping:
	def __init__(self, source, target, rest, offset):
		self.source = source
		self.target = target
		self.rest = list_to_matrix(rest)
		self.offset = list_to_matrix(offset)