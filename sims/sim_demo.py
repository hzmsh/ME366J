from tkinter import *
import time
import math
import io

ROOT_WIDTH = 800
ROOT_HEIGHT = 600
GCODE_ADDRESS = "_smileycoin.gcode"
SHOW_GUI = True

class PrintViz:
	def __init__(self, r):
		self.root = r

	def start(self):
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
		
	def print(self):
		for coor in self.c_list:
			self.getPolar(coor[0], coor[1], coor[2])
			time.sleep(0.05)
			# time.sleep(0.5)
			self.viz.root.update()

	def setCoordList(self, c):
		self.c_list = c
	
	def getPolar(self, x, y, e):
		x2 = pow(x, 2)
		y2 = pow(y, 2)
		r = pow(x2 + y2, 0.5)

		#Need to get quad of cartesion coord
		theta = math.acos(math.fabs(x)/r)
		if x < 0 and y > 0:
			theta = math.pi - theta
		if x < 0 and y < 0:
			theta += math.pi
		if x > 0 and y < 0:
			theta = 2*math.pi - theta

		if x ==0:
			if y > 0:
				theta = math.pi/2
			if y < 0:
				theta = 3*math.pi/2
		if y ==0:
			if x > 0 or x == 0:
				theta = 0
			if x < 0:
				theta = math.pi

		# print("Theta: " + str(theta))
		# print("Tan2: " + str(math.atan2(y, x)))
		# self.plot_list.append([r, theta, e])
		self.plot_list.append([r, math.atan2(y, x), e])

		# return r, theta
		self.updatePrintCanvas(r, theta)

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




if __name__ == '__main__':
	print("Sim some stuff")
	if SHOW_GUI:
		root = Tk()
		v = PrintViz(root)
		v.start()
		printer = PolarPrinter(v)
		time.sleep(1)

	coor_list = list()
	file = open(GCODE_ADDRESS, 'r')
	gcode_raw = file.read()
	gcode = gcode_raw[gcode_raw.find('Layer #1'):gcode_raw.find('Layer #2')]
	gcode_buffer = io.StringIO(gcode)
	read = True

	coor_transform = [-1300, -1000]
	coor_scale = 10
	while read:
		line = gcode_buffer.readline()
		if line:
			if line.find("G") > -1:
				if line.find("X") > -1:
					ix = line.find('X')
					x = float(line[ix+1: ix+8])
					iy = line.find('Y')
					y = float(line[iy+1: iy+8])
					x = x*coor_scale
					y = y*coor_scale
					x = x + coor_transform[0]
					y = y + coor_transform[1]

					e = False
					if line.find("G1") > -1:
						e=True
					
					coor_list.append([x, y, e])
		else:
			read = False

	if SHOW_GUI:
		printer.setCoordList(coor_list)
		printer.print()
		root.mainloop()
	