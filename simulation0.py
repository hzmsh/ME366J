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

ROOT_WIDTH = 800
ROOT_HEIGHT = 600

#GCODE PARAMETERS	
GCODE_FILE_PATH = "test_gear.gcode"

class PrintViz:
	def __init__(self, r):
		self.root = r
		self.root.wm_title("Printer Simulation")

		geo = str(ROOT_WIDTH) + "x" + str(ROOT_HEIGHT)
		self.root.geometry(geo)
		self.root.resizable(0, 0)
		self.master_frame = Frame(self.root, width=ROOT_WIDTH, height=ROOT_HEIGHT)
		self.master_frame.pack()
		# l = Label(self.master_frame, text='test')
		# l.pack()
		
		self.c0_frame = Frame(self.master_frame, width=ROOT_WIDTH*0.75, height=ROOT_HEIGHT)
		self.c1_frame = Frame(self.master_frame, width=ROOT_WIDTH*0.25, height=ROOT_HEIGHT)
		self.c0_frame.grid(row=0, column=0, padx=1, pady=1, sticky=W)
		self.c1_frame.grid(row=0, column=1, padx=1, pady=1, sticky=W)

		self.c0 = Canvas(self.c0_frame, width=ROOT_WIDTH*0.75, height=ROOT_HEIGHT*0.75, bd=3, relief="sunken")
		self.c1 = Canvas(self.c0_frame, width=ROOT_WIDTH*0.75, height=ROOT_HEIGHT*0.25, bd=3, relief="sunken")
		self.c0.pack()
		self.c1.pack()

class PolarPrinter():
	plot_list = list()
	c_list = list()
	ptf = [(ROOT_WIDTH*0.75)/2, (ROOT_HEIGHT*0.75)/2] #center of c0 canvas
	pr = 200 #radius of the print bed
	print_bed_bbox = (ptf[0]-pr, ptf[1]-pr, ptf[0]+pr, ptf[1]+pr)

	def __init__(self, v):
		self.viz = v
		self.updatePrintCanvas(0, 0)
		
	def print(self, cmd):
		cmd = cmd[1:len(cmd)-2]
		cmd = cmd.split(":")
		r = rad_stepper(cmd[1])
		theta = cmd[2]

	def rad_stepper(angle):
		return 0

	def updatePrintCanvas(self, head, theta):
		#t is the current theta of the print bed
		#x is the current position of the print head
		self.viz.c0.delete(ALL)
		self.viz.c0.create_oval(self.print_bed_bbox, fill="purple")

		#Print Bed angle line
		ll = list()
		for i in range(2):
			x = (self.pr+i*10)*math.cos(theta) + self.ptf[0]
			y = (self.pr+i*10)*math.sin(theta) + self.ptf[1]
			ll.append(x)
			ll.append(y)	
		l = tuple(ll)
		self.viz.c0.create_line(l, width=5)

		#Print new and old plotted points
		if len(self.plot_list) > 1:
			for i in range(1, len(self.plot_list)):
				coor0 = self.plot_list[i-1]
				coor1 = self.plot_list[i]
				if coor1[2]:
					px0 = coor0[0]*math.cos(theta - coor0[1]) + self.ptf[0]
					py0 = coor0[0]*math.sin(theta - coor0[1]) + self.ptf[1]
					px1 = coor1[0]*math.cos(theta - coor1[1]) + self.ptf[0]
					py1 = coor1[0]*math.sin(theta - coor1[1]) + self.ptf[1]
					p = (px0, py0, px1, py1)

					self.viz.c0.create_line(p, fill="red", width=1.5)


		#Print Head Location
		rl = list()
		# if math.cos(theta) < 0:
			# head = -1*head
		for i in range(1,3):
			x = head + pow(-1, i)*5 + self.ptf[0]
			y = pow(-1, i)*5 + self.ptf[1]
			rl.append(x)
			rl.append(y)	
		r = tuple(rl)
		self.viz.c0.create_rectangle(r, fill="blue")


if __name__ == "__main__":
	root = Tk()
	v = PrintViz(root)
	printer = PolarPrinter(v)
	while True:	
		try:
			root.update()
		except KeyboardInterrupt:
			break
