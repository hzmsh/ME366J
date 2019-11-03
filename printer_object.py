import math 
from scipy.integrate import quad

def integrand(x, r1, r2,theta1,theta2):
	

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

	# pc = [r,theta,E], this method will determine the dist we input into get_screw_angle
	def get_E_dist(self, c_old, c):
		r1 = c_old[0]
		theta1 = c_old[1]
		r2 = c[0]
		theta2 = c[1]

		if r1 > r2, theta1 < theta2:
			diff_r = r1 - r2
			diff_theta = theta2 - theta1
			r_func = r1 + (diff_r/diff_theta)*

