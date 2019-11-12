#GCODE PARSER
#-------------------------------
'''
MAIN PARSE METHOD
Input Argument: GCODE file stored as string
Output: polar coordinate list in form ([r0, theta0, e0],[r1, theta1, e1],...)

->OVERVIEW: Converting cartesian GCODE to commands for the polar printer is not simply
converting (x,y) coordinates to (r, theta) coordinates by the relationships x=rcos(theta)
and y=rsin(theta). The flaw in this reasoning is due to the differences in how cartesian
and polar printers travel between (dx, dy) and (dr, dtheta) coordinates respectively. 

Standard cartesian GCODE provides the printer with a (x_new, y_new) coordinates on every command
line. The printer is expected to find the difference between its current postion and the new
coordinate and travel to the new coordinate in a straight line. For polar printers, traveling 
over a change in polar coordinates will produce a curved line. Inorder to create the straight
lines specified by the GCODE, (dx, dy) must be converted into a function of theta. Where 
r=f(theta). r_old=f(theta_old) and r_new=f(theta_new).

To produces the r=f(theta) function, the following algorithm is used. 
1) (x_old, y_old) = (xi, yi), (x_new, y_new) = (xf, yf)
2) line1 = [A, B, C] where Ax + By = C for (dx, dy) line segment
3) segment = [xi, yi, xf, yf]
3) ti = sqrt(xi^2 + yi^2), tf = sqrt(xf^2 + yf^2) 
4) for (t = ti->tf with step_size = theta stepper resolution)
-> line2 = [D, E, F] where Dx + Ey = F for line cos(t)y = sin(t)x
-> r = intersection(line1, line2, segment)
--->intersection is found with determinant 
-> append [r, t, True] to polar coordinate list

'''

import math
import io

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
				return [x, y]

		#FIX ME
		#CATCH THIS EXCEPTION
		# print("NONE......")
		return None

def parse_gcode(g, theta_spr=800):
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

	
	#POLAR CONVERSION
	for i in range(1, len(cc[0])):
		sub_pc = []
		if not cc[2][i]:#if extrude is False
			xf2 = pow(cc[0][i], 2)
			yf2 = pow(cc[1][i], 2)
			r = pow(xf2 + yf2, 0.5)
			#tan2 determines theta based on quadrant
			theta = math.atan2(cc[1][i], cc[0][i])
			
			sub_pc.append([r, theta, 0])

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

			ti = math.atan2(yi, xi)
			tf = math.atan2(yf, xf)
			if abs(tf-ti) > math.pi:
				tf += 2*math.pi
			if tf == ti:
				direction = 0
			else:
				if tf > ti:
					direction = 1
				else:
					direction = -1

			t_step = 2*math.pi/theta_spr
			steps = math.floor(abs(tf-ti)/t_step)
			t = ti

			x_old = xi
			y_old = yi
			for j in range(steps):
				#y = mx -> y = (sin(theta)/cos(theta))*x
				#-sin(theta)x + cos(theta)y = 0
				#A=-sin(theta), B=cos(theta), C = 0
				line2 = [-math.sin(t), math.cos(t), 0]
				coor_int = intersection(line1, line2, segment)
				if coor_int:
					x_int = coor_int[0]
					y_int = coor_int[1]
					x2 = pow(x_int, 2)
					y2 = pow(y_int, 2)
					r = pow(x2+y2, 0.5)

					dx2 = pow(x_int - x_old, 2)
					dy2 = pow(y_int - y_old, 2)
					e = pow(dx2 + dy2, 0.5)

					sub_pc.append([r, t, e])
					if direction != 0:
						t += t_step*direction

					x_old = x_int
					y_old = y_int


			if (len(sub_pc) !=  0):
				pc.append(sub_pc)	

	return pc


