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
import matplotlib.animation as animation
from parse_gcode import parse_gcode
from printer_object import printer as p_obj

ROOT_WIDTH = 800
ROOT_HEIGHT = 600

#GCODE PARAMETERS	
GCODE_FILE_PATH = "sims/_smileycoin.gcode"
# GCODE_FILE_PATH = "sims/test.gcode"

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

class StepperMotor:
	event_time = 0
	error = 0
	pulse = False
	
	def __init__(self, spr):
		self.spr = spr
		self.start_time = time.time()

	def mannual_set_event_time(self, t):
		self.event_time = t
		
	def get_step_goal(self, a):
		angle = a + self.error
		theoretical = 0.5*angle*self.spr/math.pi 
		goal = round(theoretical)
		self.error = 2*math.pi*(theoretical-goal)/self.spr
		return goal 

	def execute_sync_step(self, delay):
		self.pulse = not self.pulse
		self.event_time += delay
		return [self.event_time, self.pulse]

class PolarPrinter:
	plot_x0 = []
	plot_y0 = []
	plot_x1 = []
	plot_y1 = []
	plot_x2 = []
	plot_y2 = []
	plot_x3 = []
	plot_y3 = []
	cmd_counter = 0
	steps = 100
	start_time = 0
	task_state = False
	task = []
	pre_task = []
	delay = [0, 0]
	added_delay = [0, 0]
	min_step_delay = 0.001
	min_step_delay_mag = 3
	start_time = 0
	def __init__(self, s0, s1):
		self.stepper0 = s0
		self.stepper1 = s1
		self.fig = plt.figure()
		self.ax0 = self.fig.add_subplot(2,2,1)
		self.ax1 = self.fig.add_subplot(2,2,2)
		self.ax2 = self.fig.add_subplot(2,1,2)

	def set_start_time(self):
		self.start_time = time.time()

	def set_cmds(self, c):
		self.cmds = c

	def set_task(self, c):
		self.task_state = True
		self.task = []
		s0 = c[0]
		s1 = c[1]
		# print("S0: " + str(s0) + " S1: " + str(s1))
		if s0 == 0:
			self.delay[1] = self.min_step_delay
			for i in range(2*abs(s1)):
				self.task.append([1, s1/abs(s1)])
		elif s1 == 0:
			self.delay[0] = self.min_step_delay
			for i in range(2*abs(s0)):
				self.task.append([0, s0/abs(s0)])
		else:
			ratio = abs(float(s0))/abs(float(s1))
			# print("Ratio: " + str(ratio))
			if ratio >= 1:
				self.delay[0] = self.min_step_delay
				self.delay[1] = self.min_step_delay * ratio
				s0_count = 0
				s1_count = 0
				for i in range(0, 2*abs(s0)):
					self.task.append([0, s0/abs(s0)])
					s0_count += 1
					if i >= s1_count * ratio:
						self.task.append([1, s1/abs(s1)])
						s1_count += 1
				if s1_count < 2*abs(s1):
					print("Positive Ratio -- Bad task asm")
					# self.task.append([1, s1/abs(s1)])
				# print("S0_count: " + str(s0_count) + " S1_count: " + str(s1_count))
			else:
				ratio = 1/ratio
				self.delay[0] = self.min_step_delay * ratio
				self.delay[1] = self.min_step_delay
				s0_count = 0
				s1_count = 0
				for i in range(0, 2*abs(s1)):
					self.task.append([1, s1/abs(s1)])
					s1_count += 1
					if i >= s0_count * ratio:
						self.task.append([0, s0/abs(s0)])
						s0_count += 1
				if s0_count < 2*abs(s0):
					print("Neg Ratio -- Bad task asm")

		# 		print("S0_count: " + str(s0_count) + " S1_count: " + str(s1_count))
		# print("Delay: " + str(self.delay))
		# print(self.task)
		# print("\n")
	def init_task(self):
		if self.stepper0.event_time != self.stepper1.event_time:
			if self.stepper0.event_time > self.stepper1.event_time:
				dt = self.stepper0.event_time - self.stepper1.event_time
				dt = round(dt, self.min_step_delay_mag)
				# self.stepper1.mannual_set_event_time(self.stepper0.event_time)
				self.pre_task.append([1, dt])
			elif self.stepper0.event_time < self.stepper1.event_time:
				dt = self.stepper1.event_time - self.stepper0.event_time
				dt = round(dt, self.min_step_delay_mag)
				# self.stepper0.mannual_set_event_time(self.stepper1.event_time)
				self.pre_task.append([0, dt])


	def execute_task(self):
		if len(self.pre_task) != 0:
			t = self.pre_task.pop(0)
			self.added_delay[t[0]] = t[1]
			print(self.added_delay)

		t = self.task.pop(0)
		motor = t[0]
		if len(self.task) == 0:
			self.task_state = False
		if motor == 0:
			d = self.delay[0] + self.added_delay[0]
			x = self.stepper0.execute_sync_step(d)
			self.added_delay[0] = 0
			time = round(x[0], self.min_step_delay_mag)
			return [0, time, x[1], t[1]*d]
		elif motor == 1:
			d = self.delay[0] + self.added_delay[1]
			x = self.stepper1.execute_sync_step(d)
			self.added_delay[1] = 0
			time = round(x[0], self.min_step_delay_mag)
			return [1, time, x[1], t[1]*d]

	def print(self, i):
		current = False
		if self.cmd_counter < len(self.cmds):
			if not self.task_state:
				self.set_task(self.cmds[self.cmd_counter])
				self.init_task()
				self.cmd_counter += 1

			while self.task_state:# and not current:
				data = self.execute_task()
				t = data[1]
				if t > time.time() - self.start_time:
					# print("ANIMATION IS CURRENT")
					current = True
				if data[0] == 0:
					self.plot_x0.append(data[1]*1000)
					self.plot_y0.append(not data[2])
					self.plot_x0.append(data[1]*1000)
					self.plot_y0.append(data[2])
					self.plot_x2.append(data[1]*1000)
					self.plot_y2.append(math.pi/(self.stepper0.spr * data[3]))
				elif data[0] == 1:
					self.plot_x1.append(data[1]*1000)
					self.plot_y1.append(not data[2])
					self.plot_x1.append(data[1]*1000)
					self.plot_y1.append(data[2])
					self.plot_x3.append(data[1]*1000)
					self.plot_y3.append(math.pi/(self.stepper1.spr * data[3]))

			self.ax0.clear()
			self.ax0.set_xlim(self.plot_x0[-1]-10, self.plot_x0[-1])
			self.ax0.plot(self.plot_x0, self.plot_y0)
			self.ax0.set_title('Stepper 0 Pulse')
			self.ax0.set(xlabel='Time', ylabel='State')
			self.ax1.clear()
			self.ax1.set_xlim(self.plot_x1[-1]-10, self.plot_x1[-1])
			self.ax1.plot(self.plot_x1, self.plot_y1)
			self.ax1.set_title('Stepper 1 Pulse')
			self.ax1.set(xlabel='Time', ylabel='State')
			self.ax2.clear()
			# self.ax2.set_ylim(-0.005, 0.005)
			# self.ax2.set_xlim(self.plot_x2[-1]-100, self.plot_x2[-1])
			self.ax2.plot(self.plot_x2, self.plot_y2, label="Stepper 0")
			self.ax2.plot(self.plot_x3, self.plot_y3, label="Stepper 1")
			self.ax2.set_title('Rotational Velocity')
			self.ax2.set(xlabel='Time', ylabel='rad/s')
			self.ax2.legend()

			if (self.plot_x2[-1] != self.plot_x3[-1]):
				print("x2_p: " + str(self.plot_x2[-1]))
				print("x3_p: " + str(self.plot_x3[-1]))


stepper0 = StepperMotor(800)
stepper1 = StepperMotor(800)
pp = PolarPrinter(stepper0, stepper1)

if __name__ == "__main__":
	#Get and parse GCODE to polar coordinates
	gcode = open(GCODE_FILE_PATH, 'r').read()
	coordinate_list = parse_gcode(gcode, theta_spr = stepper1.spr)
	p = p_obj(6.75,5)

	cmd_list = []
	c_old = [0, 0, False] 
	for coordinates in coordinate_list:
		for c in coordinates:
			#delta = [dr, dtheta]
			delta = [c[0] - c_old[0], c[1] - c_old[1]]
			#R ANGLE
			a0 = p.get_belt_angle(delta[0])
			s0 = stepper0.get_step_goal(a0)
			#PLATE ANGLE
			a1 = delta[1]
			s1 = stepper1.get_step_goal(a1)
			#!!!!!!!!!!!!!!!EXTRUDER ANGLE!!!!!!!!!!!
			if c[2] != 0:
				#convert distance traveled -> volume -> syringe dx -> stepper angle
				a2 = 1
			else:
				a2 = 0
			c_old = c
			cmd_list.append([s0, s1])

	# pp.set_cmds(cmd_list[20:25])
	#<0:15:10:10:0>
	print(len(cmd_list))

	# pp.set_cmds(cmd_list)
	# pp.set_start_time()

	# while True:
	# 	try:
	# 		ani = animation.FuncAnimation(pp.fig, pp.print, interval=1)
	# 		plt.show()
	# 	except KeyboardInterrupt:
	# 		break
