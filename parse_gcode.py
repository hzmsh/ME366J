#GCODE PARSER
#-------------------------------

#MAIN PARSE METHOD
#Input Argument: GCODE file stored as string
#Output: polar coordinate list in form ([r0, theta0, e0],[r1, theta1, e1],...)

import math
import io

def parse_gcode(g):
	cc = [[],[],[]] #cartesian coordinates
	pc = [] #polar coordinates
	#Take a layer of the GCODE
	gcode = g[g.find('Layer #1'):g.find('Layer #2')]
	gcode_buffer = io.StringIO(gcode)
	read = True
	#Iterate cmds and save coordinates
	while read:
		line = gcode_buffer.readline()
		if line:
			if line.find("G") > -1:
				if line.find("X") > -1:
					c = line.split()
					x = None
					y = None
					e = False
					for item in c:
						if item[0] == "X":
							x = float(item[1:])
						elif item[0] == "Y":
							y = float(item[1:])
						elif item == "G1":
							e = True
					if x != None and y != None:
						cc[0].append(x)
						cc[1].append(y)
						cc[2].append(e)
		else:
			read = False

	#Shift coordinates to be centered around (0, 0)
	x_avg = 0.5*(max(cc[0]) + min(cc[0]))
	y_avg = 0.5*(max(cc[1]) + min(cc[1]))
	cc[0] = [x - x_avg for x in cc[0]]
	cc[1] = [y - y_avg for y in cc[1]]

	#Convert to polar
	# for i in range(len(cc[0])):
	for i in range(10):
		x2 = pow(cc[0][i], 2)
		y2 = pow(cc[1][i], 2)
		r = pow(x2 + y2, 0.5)
		#tan2 determines theta based on quadrant
		theta = math.atan2(cc[1][i], cc[0][i])
		print("R: " + str(r))
		pc.append([r, theta, cc[2][i]])

	return pc

def intersection(l1, l2, s):
	error = 0.0005
	det = l1[0]*l2[1]-l1[1]*l2[0]
	#Check if parallel
	if det == 0:
		return None
	else:
		detx = l1[2]*l2[1]-l1[1]*l2[2]
		dety = l1[0]*l2[2]-l1[2]*l2[0]
		x = detx/det
		y = dety/det

		sx = [s[0], s[2]]
		sy = [s[1], s[3]]
		if min(sx) - error <= x <= max(sx) + error:
			if min(sy) -error <= y <= max(sy) + error:
				x2 = pow(x, 2)
				y2 = pow(y, 2)
				return pow(x2 + y2, 0.5)
		# print("NONE")
		# print("sXi: " + str(s[0]) + " sYi: " + str(s[1]))
		# print("sXf: " + str(s[2]) + " sYf: " + str(s[3]))
		# print(l1)
		# print(l2)	
		# print("X: " + str(x) + " Y: " + str(y))
		return None

def parse_gcode_new(g, theta_spr=200):
	cc = [[],[],[]] #cartesian coordinates
	pc = [] #polar coordinates
	#Take a layer of the GCODE
	gcode = g[g.find('Layer #1'):g.find('Layer #2')]
	gcode_buffer = io.StringIO(gcode)
	read = True
	#Iterate cmds and save coordinates
	while read:
		line = gcode_buffer.readline()
		if line:
			if line.find("G") > -1:
				if line.find("X") > -1:
					c = line.split()
					x = None
					y = None
					e = False
					for item in c:

						if item[0] == "X":
							x = float(item[1:])
						elif item[0] == "Y":
							y = float(item[1:])
						elif item == "G1":
							e = True
					if x != None and y != None:
						cc[0].append(x)
						cc[1].append(y)
						cc[2].append(e)
		else:
			read = False

	#Shift coordinates to be centered around (0, 0)
	x_avg = 0.5*(max(cc[0]) + min(cc[0]))
	y_avg = 0.5*(max(cc[1]) + min(cc[1]))
	cc[0] = [x - x_avg for x in cc[0]]
	cc[1] = [y - y_avg for y in cc[1]]

	#NEW METHOD OF POLAR CONVERSION
	#r = f(theta)
	#theta is independent and increments by step resolution
	old_direction = None
	for i in range(1, len(cc[0])):
	# for i in range(1, 100):
		if not cc[2][i]:#if extrude is false
			xf2 = pow(cc[0][i], 2)
			yf2 = pow(cc[1][i], 2)
			r = pow(xf2 + yf2, 0.5)
			#tan2 determines theta based on quadrant
			theta = math.atan2(cc[1][i], cc[0][i])
			pc.append([r, theta, False])

		else: #if extrude is true
			#Create line segment from points (x1, y1) and (x2, y2)
			#Save line segment in standard form Ax + By = C
			xi = cc[0][i-1]
			yi = cc[1][i-1]
			xf = cc[0][i]
			yf = cc[1][i]
			segment = [xi, yi, xf, yf]

			if xf == xi: #vertical slope
				line1 = [1, 0, xi] #(1)x +(0)y = (xi)
			else:
				#y-yi = m(x-xi)
				#-mx + y = yi - mxi
				#A=-m, B=1, C = yi - mxi
				m = (yf-yi)/(xf-xi)
				line1 = [-m, 1, yi - m*xi]

			# xi2 = pow(cc[0][i-1], 2)
			# yi2 = pow(cc[1][i-1], 2)
			# ri = pow(xi2 + yi2, 0.5)
			# print(ri)
			ti = math.atan2(yi, xi)
			tf = math.atan2(yf, xf)
			if tf == ti:
				direction = 0
			else:
				direction = (tf-ti)/abs(tf-ti)
			# print("TF: " + str(tf))
			# print("Ti: " + str(ti))
			# print("Dir: " + str(direction))
			t_step = 2*math.pi/theta_spr
			steps = math.floor(abs(tf-ti)/t_step)
			t = ti
			# if direction < 0:
			# 	t = tf

			for j in range(steps):
				line2 = [-math.sin(t), math.cos(t), 0]
				
				r = intersection(line1, line2, segment)
				if direction != 0:
					t += t_step*direction
				# print(t)
				if r:
					print(r)
					if r > 0:
						pc.append([r, t, True])
				


			#y = mx -> y = (sin(theta)/cos(theta))*x
			#-sin(theta)x + cos(theta)y = 0
			#A=-sin(theta), B=cos(theta), C = 0
		


			#OLD STUFF
			# # print("Ti: " + str(ti))
			# # print("Tf: " + str(tf))
			# dt = tf-ti
			# if abs(dt) > math.pi:
			# 	if (dt < 0):
			# 		dt += 2*math.pi
			# 	elif (dt > 0):
			# 		dt -= 2*math.pi
				
			# direction = 0
			# if (dt == 0): #Handel Case
			# 	print("HELP delta theta = 0")
			# elif (dt < 0):
			# 	direction = -1
			# elif (dt > 0):
			# 	direction = 1


			# t_step = 2*math.pi/theta_spr
			# steps = int(abs(dt)/t_step)
			# # print("Xi " + str(xi))
			# # print("Yi " + str(yi))
			# # print("m " + str(m))
			# # print("steps " + str(steps))
			# # print("Ri: " + str(ri))
			# # print("Ti: " + str(ti))
			# # print("Dir: " + str(direction))
			# # print("step: " + str(t_step))
			# # for i in range(0, steps+2):
			# # 	t = ti + i*t_step*direction
			# # 	r = abs((yi + m*xi)/(m*abs(math.cos(t))-abs(math.sin(t))))
			# # 	print("R: " + str(r))
			# # 	# print("T: " + str(t))
				
			# # 	pc.append([r, t, True])
			# for i in range(0, steps+2):
			# 	t = ti + i*t_step*direction
			# 	a = math.cos(t)
			# 	b = ri*math.cos(ti)
			# 	c = math.sin(t)
			# 	d = ri*math.sin(ti)
			# 	r = abs((b-m*d)/(m*c-a))
			# 	print("R: " + str(r))
			# 	pc.append([r, t, True])

	# print(pc)
	# print("\n\n\n\n\n")
	return pc


