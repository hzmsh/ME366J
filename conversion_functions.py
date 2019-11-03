#CONVERSION FUNCTIONS
#--------------------

'''
This file contains functions that convert general movement goals (ex. delta 
radius, delta volume...) into angle goals (in radians) to send to the stepper motors

TODO
-Belt Conversion
-Lead Screw Conversion
	-Z axis
	-Extruder

'''

#Belt Distance -> Angle
import math 

def get_belt_angle(dist, pulley_radius):
    # theta = arc_length / r, angle in radian
    belt_angle = dist / pulley_radius
    return (belt_angle)

#Screw Distance -> Angle
def get_screw_angle(dist, screw_pitch):
	# angle in radian
	num_circles = dist / screw_pitch
	screw_angle = num_circles * 2 * math.pi
	return (screw_angle)