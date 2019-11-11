#SIMULATION FOR POLAR 3D PRINTER

'''
TO DO LIST....
-Printer Object
	-independent and depented variabels
	-contain step converter
-GCODE Parser
	-gcode -> polar coordinates
-Step Converter
	-polar coordinates -> motor steps
-Visualizer
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
# from parse_gcode import parse_gcode_old as parse_gcode
from parse_gcode import parse_gcode
from printer_object import printer as p_obj

ROOT_WIDTH = 800
ROOT_HEIGHT = 600
THETA_SPR = 200

#GCODE PARAMETERS	
# GCODE_FILE_PATH = "sims/_smileycoin.gcode"
GCODE_FILE_PATH = "sims/test.gcode"
# com = serial.Serial(port="COM7", baudrate=9600, timeout=1)
# empty = com.readline()
# com.flushOutput()
# com.flushInput()
com = None

def send_serial(data):
	print(data)
	com.flushOutput()
	com.flushInput()
	com.write(data.encode())

if __name__ == "__main__":
	#Get and parse GCODE to polar coordinates
	gcode = open(GCODE_FILE_PATH, 'r').read()
	coordinate_list = parse_gcode(gcode)
	p = p_obj(6.75, 5)

	cmd_list = []
	c_old = [0, 0, False] 
	for c in coordinate_list:
		#delta = [dr, dtheta]
		delta = [c[0] - c_old[0], c[1] - c_old[1]]
		#R ANGLE
		a0 = p.get_belt_angle(delta[0])
		#PLATE ANGLE
		a1 = delta[1]

		#!!!!!!!!!!!!!!!EXTRUDER ANGLE!!!!!!!!!!!
		if c[2] != 0:
			#convert distance traveled -> volume -> syringe dx -> stepper angle
			a2 = 1
		else:
			a2 = 0

		c_old = c
		cmd_string = "<" + str(0)
		cmd_string += ":" + str(a0)
		cmd_string += ":" + str(a1) + ">"
		cmd_list.append(cmd_string)


	# for c in cmd_list:
	# 	print(c)

	