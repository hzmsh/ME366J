#MAIN PROGRAM FOR ME366J PROJECT
#-------------------------------

'''
OVERVIEW:

This is the main function for the projects python code. The purpose is
to act as the user interface, handle gcode, anc comunicate with the 
printer's arduino MEGA. 

!!!!!!!CONSTRUCTION!!!!!!!!!!

Functions and classes can exist in this file but should be imported if they
become too large. It may be benifical to import functions and classes to make
collaboration easier.

NOTES: 
(Place development notes here)

MASTER TODO LIST (Feel free to add anything you think of)
-Printer Object
	-independent and depented variabels
	-contain step converter
	-contain actuator information
-Step Converter
	-polar coordinates -> motor steps
-User Interface
	-steps sizes
	-error
	-print

'''
from tkinter import *
import time
import math
import io
import numpy as np 
import matplotlib.pyplot as plt

from parse_gcode import parse_gcode
from conversion_functions import get_belt_angle, get_screw_angle

#GCODE PARAMETERS	
GCODE_FILE_PATH = "sims/test_gear.gcode"

if __name__ == "__main__":
	#Get and parse GCODE to polar coordinates
	gcode = open(GCODE_FILE_PATH, 'r').read()
	coordinate_list = parse_gcode(gcode)

	#Turn polar coordinates into motor command strings
	cmd_list = []
	c_old = [0, 0, False]
	for c in coordinate_list:
		#delta = [dr, dtheta]
		delta = [c[0] - c_old[0], c[1] - c_old[1]]
		a0 = get_belt_angle(delta[0]) #radius angle
		a1 = delta[1] #plate angle
		if c[2]:
			#NOTE: SCREW ANGLE DEPENDS ON TRAVEL DISTANCE...
			#MORE WORK NEEDED
			a2 = get_screw_angle() #extruder angle
		else:
			a2 = 0

		#cmd_list.append(create_cmd_sting(a0, a1, a2))





