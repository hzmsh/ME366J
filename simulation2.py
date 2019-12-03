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
	plot_x4 = []
	plot_y4 = []
	plot_x5 = []
	plot_y5 = []
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
	r_pos = 0
	r_pulley = 8
	def __init__(self, title, s0, s1):
		self.stepper0 = s0
		self.stepper1 = s1
		self.fig = plt.figure()
		self.fig.subplots_adjust(hspace=0.5)
		self.fig.suptitle(title, fontsize=16)
		self.ax0 = self.fig.add_subplot(3,2,1)
		self.ax1 = self.fig.add_subplot(3,2,2)
		self.ax2 = self.fig.add_subplot(3,1,2)
		self.ax3 = self.fig.add_subplot(3,1,3)

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

		t = self.task.pop(0) #t[0] = motor_id, t[1] = motor direction
		motor = t[0]
		if len(self.task) == 0:
			self.task_state = False
		if motor == 0:
			d = self.delay[0] + self.added_delay[0]
			x = self.stepper0.execute_sync_step(d) #x[0] = time, x[1] = pulse
			self.added_delay[0] = 0
			time = round(x[0], self.min_step_delay_mag)
			return [0, time, x[1], t[1]*d] #motor_id, time, pulse, direction*total delay
		elif motor == 1:
			d = self.delay[1] + self.added_delay[1]
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
				if data[0] == 0: #Handle data retruned for Radial Stepper
					self.plot_x0.append(data[1])
					self.plot_y0.append(not data[2])
					self.plot_x0.append(data[1])
					self.plot_y0.append(data[2])
					self.plot_x2.append(data[1])
					#Stepper 0 spr = 6400[steps/ rev] or 12800[pulse/rev]
					#w [rad/s] = 6400/2pi [steps/ rad] or 6400/pi [pulse/rad]
					self.plot_y2.append(math.pi/(self.stepper0.spr * data[3]))
					self.r_pos += abs(data[3])/data[3] * (math.pi * self.r_pulley /self.stepper0.spr)
					print(self.r_pos)
						
				elif data[0] == 1: #Handle data retruned for Theta Stepper
					self.plot_x1.append(data[1])
					self.plot_y1.append(not data[2])
					self.plot_x1.append(data[1])
					self.plot_y1.append(data[2])
					self.plot_x3.append(data[1])
					self.plot_y3.append(math.pi/(self.stepper1.spr * data[3]))

				if len(self.plot_y2)!= 0 and len(self.plot_y3)!=0:
					vplate = self.r_pos * self.plot_y3[-1]
					vradial = self.r_pulley * self.plot_y2[-1]
					v = pow(pow(vplate, 2) + pow(vradial, 2), 0.5)
					self.plot_y4.append(v)
					if data[0] == 0:
						self.plot_x4.append(self.plot_x0[-1])
					else:
						self.plot_x4.append(self.plot_x1[-1])

			self.ax0.clear()
			self.ax0.set_xlim(self.plot_x0[-1]-0.01, self.plot_x0[-1])
			self.ax0.plot(self.plot_x0, self.plot_y0)
			self.ax0.set_title('Stepper 0 Pulse')
			self.ax0.set(xlabel='Time [sec]', ylabel='State')
			self.ax1.clear()
			self.ax1.set_xlim(self.plot_x1[-1]-0.01, self.plot_x1[-1])
			self.ax1.plot(self.plot_x1, self.plot_y1)
			self.ax1.set_title('Stepper 1 Pulse')
			self.ax1.set(xlabel='Time [sec]', ylabel='State')
			# self.ax2.set_ylim(-0.005, 0.005)
			# self.ax2.set_xlim(self.plot_x2[-1]-100, self.plot_x2[-1])
			self.ax2.clear()
			self.ax2.plot(self.plot_x2, self.plot_y2, label="Stepper 0")
			self.ax2.plot(self.plot_x3, self.plot_y3, label="Stepper 1")
			self.ax2.set_title('Rotational Velocity')
			self.ax2.set(xlabel='Time [sec]', ylabel='w [rad/s]')
			self.ax2.legend()

			self.ax3.clear()
			# self.ax3.set_ylim(3, 5)
			# self.ax3.set_ylim(max(self.plot_y4)*0.5, max(self.plot_y4))
			self.ax3.plot(self.plot_x4, self.plot_y4, label="Print Head Velocity")
			self.ax3.set_title('Relative Print Head Velocity')
			self.ax3.set(xlabel='Time [sec]', ylabel='V [mm/s]')
			# self.ax3.legend()

stepper0 = StepperMotor(6400)
stepper1 = StepperMotor(6400)
title = "20+10*t"
pp = PolarPrinter(title, stepper0, stepper1)

if __name__ == "__main__":
	#Get and parse GCODE to polar coordinates
	gcode = open(GCODE_FILE_PATH, 'r').read()
	p = p_obj(8,5)

	cmd_list = []
	c_old = [0, 0, False] 
	left_bound = 0.0
	right_bound = math.pi
	#Print resolution used to approximate polar function
	#(This is not the resolution fo the stepper motor)
	theta_resolution = 2*math.pi/1600
	iterations = round((right_bound-left_bound)/theta_resolution)
	t0 = 0
	t1 = 0
	r0 = 0
	r1 = 0
	for i in range(iterations):
		#Increase theta by resolution for each iteration
		t1 += theta_resolution
		#r = f(theta), function will be hard coded for the simulation
		r1 = 20+10*t1
		# r1 = abs(100*math.sin(2*t1))
		#deltas are used to get steps
		dr = r1 - r0;
		dr = p.get_belt_angle(dr) 
		dt = t1 - t0; #Really just the theta resolution
		cmd_list.append([stepper0.get_step_goal(dr), stepper1.get_step_goal(dt)])
		r0 = r1
		t0 = t1

	pp.set_cmds(cmd_list)
	pp.set_start_time()

	while True:
		try:
			ani = animation.FuncAnimation(pp.fig, pp.print, interval=1)
			plt.show()
		except KeyboardInterrupt:
			break
