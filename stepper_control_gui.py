from tkinter import *
import time
import math
import io
import serial

ROOT_WIDTH = 800
ROOT_HEIGHT = 600
NUMBER_OF_STEPPERS = 2

driver_list = ["TB6600", "TB6600", "TB6600", "TB6600"]
function_list = ["rail", "extruder", "?", ">"]
pin_list = [[49, 51, 53], [48, 50, 51], [1, 2, 3], [1, 2, 3]]
spr_list = [800, 800, 800, 800]

com = serial.Serial(port="COM7", baudrate=9600, timeout=1)
empty = com.readline()
com.flushOutput()
com.flushInput()

class Stepper():
	def __init__(self, dtype, f, pins, spr, angle=0, speed=100):
		self.driver_type = dtype
		self.function = f
		self.pins = pins
		self.spr = spr
		self.angle=angle
		self.speed=speed

class StepperGUI:
	def __init__(self, r, s):
		self.root = r
		self.root.wm_title("Stepper Control Panel")

		geo = str(ROOT_WIDTH) + "x" + str(ROOT_HEIGHT)
		self.root.geometry(geo)
		self.root.resizable(0, 0)
		self.master_frame = Frame(self.root, width=ROOT_WIDTH, height=ROOT_HEIGHT)
		self.master_frame.grid()
		self.master_frame.grid_columnconfigure(0, minsize=ROOT_WIDTH*0.5) 
		self.master_frame.grid_columnconfigure(1, minsize=ROOT_WIDTH*0.5) 

		#Stepper Frames	
		self.s_frame = []
		layout = [[0, 0], [0, 1], [1, 0], [1, 1]]
		for i in range(len(s)):
			#Setup Frames
			self.master_frame.grid_rowconfigure(i, minsize=ROOT_HEIGHT/len(s))
			sf = Frame(self.master_frame, width=ROOT_WIDTH*0.75, height=ROOT_HEIGHT*0.5, bd=3, relief="raised")
			sf.grid(row=layout[i][0], column=layout[i][1], padx=1, pady=1, sticky=N+W)
			sf.grid_columnconfigure(0, minsize=ROOT_WIDTH*0.49)
			title = Label(sf, text="Stepper " + str(i) + " (" +s[i].function + ")")
			title.grid(row=0, sticky=W)
			content = Frame(sf, bd=3, relief="sunken")
			content.grid(row=1, sticky=W)

			#Setup Widgets (Place dynamic widgets in dictionary)
			s_widget ={}
			self.s_frame.append(s_widget)
			content.grid_columnconfigure(0, minsize=ROOT_WIDTH*0.75*0.25)
			Label(content, text="Driver: " + str(s[i].driver_type)).grid(row=0, column=0, sticky=W)
			Label(content, text="Arduino Pins: " + str(s[i].pins)).grid(row=1, column=0, sticky=W)
			Label(content, text="SPR: " + str(s[i].spr)).grid(row=2, column=0, sticky=W)
			Label(content, text="------------").grid(row=3, column=0, sticky=W)
			angle_var = StringVar()
			angle_var.set("Angle: " + str(s[i].angle))
			s_widget["angle"] = angle_var
			Label(content, textvariable=self.s_frame[i]["angle"]).grid(row=4, column=0, sticky=W)
			speed_var = StringVar()
			speed_var.set("Speed: "+str(s[i].speed)+"%")
			s_widget["speed"] = speed_var
			Label(content, textvariable=self.s_frame[i]["speed"]).grid(row=5, column=0, sticky=W)

			Label(content, text="Set Speed", font='Helvetica 8 bold').grid(row=0, column=1, sticky=W)
			speed_scale = Scale(content, from_=0, to=100, orient=HORIZONTAL, width=20)
			speed_scale.set(s[i].speed)
			speed_scale.grid(row=0, column=2, sticky=N+W)
			s_widget["speed_scale"] = speed_scale
			Label(content, text="Set Goal (revs)", font='Helvetica 8 bold').grid(row=1, column=1)
			goal_entry = Entry(content)
			goal_entry.insert(0, "0")
			goal_entry.grid(row=1, column=2, sticky=W)
			s_widget["goal"] = goal_entry

		#Button Frames
		bf = Frame(self.master_frame, width=ROOT_WIDTH*0.25)
		bf.grid(row=layout[len(s)-1][0]+1, column=0, columnspan=2, padx=1, pady=1, sticky=N+W)
		Button(bf, text="Send Motor CMD", command=self.command_callback).pack()

		self.stepper_list = s

	def command_callback(self):
		speed_check = False
		speed_string= "<1:"
		for i in range(len(self.stepper_list)):
			speed = self.s_frame[i]["speed_scale"].get()
			speed_string += str(speed)
			self.s_frame[i]["speed"].set("Speed: "+str(speed)+"%")
			if self.stepper_list[i] != speed:
				speed_check = True
			if i != len(self.stepper_list)-1:
				speed_string += ":"
		speed_string += ">"
		if speed_check:
			self.send_serial(speed_string)

		time.sleep(0.5)

		goal_check = False
		goal_string = "<0:"
		for i in range(len(self.stepper_list)):
			rev = float(self.s_frame[i]["goal"].get())
			if rev != 0:
				goal_check = True
			angle = rev * 2*math.pi
			goal_string += str(angle)
			if i != len(self.stepper_list)-1:
				goal_string += ":"
		goal_string += ">"
		if goal_check:
			self.send_serial(goal_string)


	def send_serial(self, data):
		print(data)
		com.flushOutput()
		com.flushInput()
		com.write(data.encode())


if __name__ == "__main__":
	s_list = []
	for i in range(NUMBER_OF_STEPPERS):
		s_list.append(Stepper(driver_list[i], function_list[i], pin_list[i], spr_list[i]))

	root = Tk()
	v = StepperGUI(root, s_list)
	while True:	
		try:
			root.update()
		except KeyboardInterrupt:
			break
