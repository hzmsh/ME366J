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
import serial

from parse_gcode import parse_gcode
from printer_object import printer as p_obj

#GCODE PARAMETERS	
GCODE_FILE_PATH = "sims/test.gcode"
SPR = [800, 200, 200, 200]

def getSteps(goal, error, spr):
	angle_goal = goal + error
	step_goal_float = 0.5*angle_goal*spr/math.pi
	step_goal = round(step_goal_float)
	error = 2*math.pi*(step_goal_float - step_goal)/spr
	return [step_goal, error]


if __name__ == "__main__":
	#Get and parse GCODE to polar coordinates
	gcode = open(GCODE_FILE_PATH, 'r').read()
	coordinate_list = parse_gcode(gcode)
	p = p_obj(20,5)

	cmd_list = []
	c_old = [0, 0, False]
	a = [0, 0, 0, 0]
	error = [0, 0, 0, 0]
	for c in coordinate_list:
		#delta = [dr, dtheta]
		delta = [c[0] - c_old[0], c[1] - c_old[1]]
		
		#GET STEPPER MOTOR ANGLES
		#------------------------
		#R ANGLE
		a[0] = p.get_belt_angle(delta[0])
		#PLATE ANGLE
		a[1] = delta[1]
		#!!!!!!!!!!!!!!!EXTRUDER ANGLE!!!!!!!!!!!
		if c[2] != 0:
			#convert distance traveled -> volume -> syringe dx -> stepper angle
			a[2] = 1
		else:
			a[2] = 0

		#CONVERT ANGLES TO STEPS
		#-----------------------
		step = [0, 0, 0, 0]
		for i in range(len(a)):
			s = getSteps(a[i], error[i], SPR[1])
			step[i] = s[0]
			error[i] = s[1]

		c_old = c
		cmd_string = "<" + str(0)
		cmd_string += ":" + str(step[0])
		cmd_string += ":" + str(step[1])
		cmd_string += ":" + str(step[2]) + ">"
		print(cmd_string)
		cmd_list.append(cmd_string)


	while True:	
		try:
			time.sleep(0.1)
		except KeyboardInterrupt:
			break