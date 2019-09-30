from tkinter import *
import time
import math

ROOT_WIDTH = 800
ROOT_HEIGHT = 600

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
		

	def setCoordList(self, c):
		self.c_list = c
	
	def getPolar(self, x, y):
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

		print("X: " + str(x))
		print("Y: " + str(y))
		print("R: " + str(r))
		print("Theta: " + str(theta))
		self.plot_list.append([r, theta])

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
		for coor in self.plot_list:
			px = coor[0]*math.cos(theta - coor[1])
			py = coor[0]*math.sin(theta - coor[1])
			pl = list()
			for i in range(1,3):
				x = px + pow(-1, i)*2 + self.ptf[0]
				y = py + pow(-1, i)*2 + self.ptf[1]
				pl.append(x)
				pl.append(y)	
			p = tuple(pl)
			self.viz.c0.create_oval(p, fill="red")


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
	print("Going to do some polar stuff...")
	root = Tk()
	v = PrintViz(root)
	v.start()
	printer = PolarPrinter(v)
	time.sleep(1)

	# coor_list = [[-100, 100], [-75, 100], [-50, 100]]
	coor_list = list()
	for i in range(25):
		coor_list.append([100 - i*8, 100])
	for i in range(25):
		coor_list.append([-100, 100 - i*8])
	for i in range(25):
		coor_list.append([-100 + i*8, -100])
	for i in range(25):
		coor_list.append([100, -100 + i*8])
	for coor in coor_list:
		printer.getPolar(coor[0], coor[1])
		time.sleep(0.05)
		root.update()
	for coor in coor_list:
		printer.getPolar(coor[0]*0.75, coor[1]*0.75)
		time.sleep(0.05)
		root.update()

	root.mainloop()
	