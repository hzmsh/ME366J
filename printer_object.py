import math 

class printer():
	def __init__(self, pulley_radius,screw_pitch):
		self.pulley_radius = pulley_radius
		self.screw_pitch = screw_pitch

	def get_belt_angle(self, dist):
	    # theta = arc_length / r, angle in radian
	    belt_angle = dist / self.pulley_radius
	    return (belt_angle)

	#Screw Distance -> Angle
	def get_screw_angle(self, dist):
		# angle in radian
		num_circles = dist / self.screw_pitch
		screw_angle = num_circles * 2 * math.pi
		return (screw_angle)



