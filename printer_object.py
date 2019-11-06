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

	# c = [r,theta,E], this method will determine the dist we input into get_screw_angle
	def get_E_dist(self, c_old, c):
		r1 = c_old[0]
		theta1 = c_old[1]
		r2 = c[0]
		theta2 = c[1]

		# convert r,theta to x,y
		x1 = r1*(math.cos(theta1))
		y1 = r1*(math.sin(theta1))
		x2 = r2*(math.cos(theta2))
		y2 = r2*(math.sin(theta2))	

		# midpoint coord
		# consider three senarios, x1,x2 both posi, both nega, one posi + one nega
 		x3 = abs(x1-x2)/2 + min(x1,x2)
  		y3 = abs(y1-y2)/2 + min(y1,y2)

		#compute dist
		dist1 = math.sqrt((x1-x3)^2+(y1-y3)^2)
		dist2 = math.sqrt((x2-x3)^2+(y2-y3)^2)
		dist = dist1 + dist2

		# call get_screw_angle
		screw_angle = self.get_screw_angle(dist)
		return (screw_angle)                  