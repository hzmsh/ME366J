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
	for i in range(len(cc[0])):
		x2 = pow(cc[0][i], 2)
		y2 = pow(cc[1][i], 2)
		r = pow(x2 + y2, 0.5)
		#tan2 determines theta based on quadrant
		theta = math.atan2(cc[1][i], cc[0][i])
		pc.append([r, theta, cc[2][1]])

	return pc



