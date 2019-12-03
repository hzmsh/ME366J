from tkinter import *
import time
import math
import io
import serial
from copy import copy

ROOT_WIDTH = 200
ROOT_HEIGHT = 600
LAYER_LIMIT = 10

#Setup Serial Com
com = serial.Serial(port="COM7", baudrate=9600, timeout=1)
empty = com.readline()
com.flushOutput()
com.flushInput()

def sendSerial(data):
	print(data)
	com.flushOutput()
	com.flushInput()
	com.write(data.encode())
	time.sleep(0.25)

class PolarFunctionStructure:
	function_type = 0
	amplitude = 0
	frequency = 0
	power = 0
	time_shift = 0
	vertical_shift = 0
	left_bound = 0
	right_bound = 0

#TKINTER Stuff.....
root = Tk()
current_function = PolarFunctionStructure()
function = [[] for i in range(LAYER_LIMIT)]
layer_text_list = [[] for i in range(LAYER_LIMIT)]

def circleCB():
	fun_title_var.set("Function (Circle)")
	current_function.function_type = 0
def spiralCB():
	fun_title_var.set("Function (Spiral)")
	current_function.function_type = 1
def sinCB():
	fun_title_var.set("Function (Sine)")
	current_function.function_type = 2
def absSinCB():
	fun_title_var.set("Function (Abs Sine)")
	current_function.function_type = 3
def cosCB():
	fun_title_var.set("Function (Cosine)")
	current_function.function_type = 4
def absCosCB():
	fun_title_var.set("Function (Abs Cosine)")
	current_function.function_type = 5

#Master Frame holds all content
master_frame = Frame(root, width=ROOT_WIDTH, height = ROOT_HEIGHT)
master_frame.grid(row=0, column=0, padx=1, pady=1)

#CTRL FRAME
#----------
ctrl_title = Label(master_frame, text="Layer Customizer", font='Helvetica 10 bold')
ctrl_title.grid(row=0, column=0, padx=1, pady=1)
ctrl_width = int(ROOT_WIDTH/8)
ctrl_frame = Frame(master_frame, bd=2.5, relief=SUNKEN)
master_frame.grid_columnconfigure(0, minsize=ctrl_width)
ctrl_frame.grid(row=1, column=0, padx=1, pady=1)
#function selection
fun_title_var = StringVar()
fun_title_var.set("Function")
fun_title = Label(ctrl_frame, textvariable=fun_title_var).pack(anchor='w')

b_width = int(ctrl_width*0.75)
cirlce_button = Button(ctrl_frame, text="Circle", width=b_width, command=circleCB).pack()
spiral_button = Button(ctrl_frame, text="Spiral", width=b_width, command=spiralCB).pack()
sin_button = Button(ctrl_frame, text="Sine", width=b_width, command=sinCB).pack()
abs_sin_button = Button(ctrl_frame, text="Abs Sine", width=b_width, command=absSinCB).pack()
cos_button = Button(ctrl_frame, text="Cosine", width=b_width, command=cosCB).pack()
abs_cos__button = Button(ctrl_frame, text="Abs Cosine", width=b_width, command=absCosCB).pack()
#function parameters
Label(ctrl_frame, text="Function Parameters").pack(anchor='w')
Label(ctrl_frame, text="Amplitude", font='Helvetica 8 italic').pack(anchor='w')
amp_default = StringVar()
amp_entry = Entry(ctrl_frame, width=ctrl_width, textvariable=amp_default)
amp_entry.pack(anchor='w')
Label(ctrl_frame, text="Frequency", font='Helvetica 8 italic').pack(anchor='w')
freq_default = StringVar()
freq_entry = Entry(ctrl_frame, width=ctrl_width, textvariable=freq_default)
freq_entry.pack(anchor='w')
Label(ctrl_frame, text="Time Shift", font='Helvetica 8 italic').pack(anchor='w')
time_default = StringVar()
time_entry = Entry(ctrl_frame, width=ctrl_width, textvariable=time_default)
time_entry.pack(anchor='w')
Label(ctrl_frame, text="Vertical Shift", font='Helvetica 8 italic').pack(anchor='w')
vert_default = StringVar()
vert_entry = Entry(ctrl_frame, width=ctrl_width, textvariable=vert_default)
vert_entry.pack(anchor='w')
Label(ctrl_frame, text="Left Bound", font='Helvetica 8 italic').pack(anchor='w')
left_default = StringVar()
left_entry = Entry(ctrl_frame, width=ctrl_width, textvariable=left_default)
left_entry.pack(anchor='w')
Label(ctrl_frame, text="Right Bound", font='Helvetica 8 italic').pack(anchor='w')
right_default = StringVar()
right_entry = Entry(ctrl_frame, width=ctrl_width, textvariable=right_default)
right_entry.pack(anchor='w')
#set defaults
#layer parameters
Label(ctrl_frame, text="Layer Specification").pack()
Label(ctrl_frame, text="First Layer", font='Helvetica 8 italic').pack(anchor='w')
lay0_default = StringVar()
lay0_entry = Entry(ctrl_frame, width=ctrl_width, textvariable=lay0_default)
lay0_entry.pack(anchor='w')
Label(ctrl_frame, text="Last Layer", font='Helvetica 8 italic').pack(anchor='w')
lay1_default = StringVar()
lay1_entry = Entry(ctrl_frame, width=ctrl_width, textvariable=lay1_default)
lay1_entry.pack(anchor='w')

def ctrlReset():
	amp_default.set('50')
	freq_default.set('1')
	time_default.set('0')
	vert_default.set('0')
	left_default.set('0')
	right_default.set('6.2832')
	lay0_default.set('0')
	lay1_default.set('0')
	current_function = PolarFunctionStructure()

ctrlReset()
#----------

#LAYOUT FRAME
#----------
layer_title = Label(master_frame, text="Layer Visualizer", font='Helvetica 10 bold')
layer_title.grid(row=0, column=1, padx=1, pady=1)
layout_frame = Frame(master_frame, bd=2.5, relief=SUNKEN)
layout_width = int(ROOT_WIDTH/2)
master_frame.grid_columnconfigure(1, minsize=layout_width)
layout_frame.grid(row=1, column=1, padx=1, pady=1, sticky='n')
Label(layout_frame, text="Layers").pack(anchor='w')
layer_text = Text(layout_frame, height=25, width=int(layout_width*0.95))
layer_text.pack()
#----------

#PRINT FRAME
#----------
print_frame_title = Label(master_frame, text="Print Commander", font='Helvetica 10 bold')
print_frame_title.grid(row=0, column=2, padx=1, pady=1)
print_frame = Frame(master_frame, bd=2.5, relief=SUNKEN)
print_frame_width = ctrl_width
master_frame.grid_columnconfigure(2, minsize=print_frame_width)
print_frame.grid(row=1, column=2, padx=1, pady=1, sticky='n')
Label(print_frame, text="Serial Commands").pack(anchor='w')
#----------

def resetEverything():

	for i in range(LAYER_LIMIT):
		function[i].clear()
		layer_text_list[i].clear()
	# function = [[] for i in range(LAYER_LIMIT)]
	# layer_text_list = [[] for i in range(LAYER_LIMIT)]
	layer_text.delete(1.0, END)
	ctrlReset()

#Layer Submission
def submitCB():
	current_function.amplitude = amp_entry.get()
	current_function.frequency = freq_entry.get()
	current_function.time_shift = time_entry.get()
	current_function.vertical_shift = vert_entry.get()
	current_function.left_bound = left_entry.get()
	current_function.right_bound = right_entry.get()

	l_begin = int(lay0_entry.get())
	l_end = int(lay1_entry.get())

	#build function string
	f = current_function.function_type
	f_str = ''
	f_str0 = current_function.amplitude
	f_str1 = current_function.frequency + '(t - ' + current_function.time_shift + ')'
	f_str2 = ' + ' + current_function.vertical_shift
	f_str3 = ' for [' + current_function.left_bound + ', ' + current_function.right_bound + ']'
	if f == 0: #circle
		f_str = f_str0 + f_str3 
	elif f == 1: #spiral
		f_str = f_str0 + ' * ' + f_str1 + f_str2 + f_str3
	elif f == 2: #sine
		f_str = f_str0 + ' * sin(' + f_str1 + ') ' + f_str2 + f_str3
	elif f == 3: #abs sine
		f_str = f_str0 + ' * |sin(' + f_str1 + ')| ' + f_str2 + f_str3
	elif f == 4: # cosine
		f_str = f_str0 + ' * cos(' + f_str1 + ') ' + f_str2 + f_str3
	elif f == 5: # abs cosine
		f_str = f_str0 + ' * |cos(' + f_str1 + ')| ' + f_str2 + f_str3

	for i in range(l_begin, l_end+1):
		layer_text_list[i].append(f_str)
		function[i].append(copy(current_function))
	layer_text.delete(1.0, END)
	layer_count = 0
	for layer in layer_text_list:
		if len(layer) > 0:
			layer_text.insert(END, 'LAYER:  ' + str(layer_count) + '\n')
			for f in layer:
				layer_text.insert(END, f + '\n')
		layer_count += 1


def setupPrint():
	if len(function[0]) == 0:
		print_in_progress = False
		return False
	return True


def sendPrint():
	layer_count = 0
	for layer in function:
		if len(layer) > 0:
			for f in layer:
				sendSerial('<1>')
				output = '<2:'
				output += str(f.function_type) + ':'
				output += f.amplitude + ':'
				output += f.frequency + ':'
				output += f.time_shift + ':'
				output += f.vertical_shift + ':'
				output += f.left_bound + ':'
				output += f.right_bound + ':'
				output += str(layer_count)+ '>'
				sendSerial(output)
		layer_count += 1 
	sendSerial('<3>')
	return True

def getFeedback():
	if com.in_waiting:  # Or: while ser.inWaiting():
		line = com.readline().strip().decode("utf-8")
		if line == '<Done>':
			return False
	return True

def startPrint():
	print_in_progress = True
	print_stage = 0
	while print_in_progress:
		if print_stage == 0:
			print_in_progress = setupPrint()
			print_stage += 1
		elif print_stage == 1:
			print_in_progress = sendPrint()
			print_stage += 1
		elif print_stage == 2:
			print_in_progress = getFeedback()

def toggleE():
	sendSerial('<4>')

def toggleZ():
	sendSerial('<5>')

#IMPORT BUTTONS
ctrl_sub_button = Button(ctrl_frame, text="Submit", width=int(0.5*b_width), command=submitCB).pack(side=LEFT)
ctrl_reset_button = Button(ctrl_frame, text="Reset", width=int(0.5*b_width), command=ctrlReset).pack(side=RIGHT)
start_print_button = Button(print_frame, text="Start Print", width=int(b_width), command=startPrint).pack()
reset_everything_button = Button(print_frame, text="Clear", width=int(b_width), command=resetEverything).pack()
toggle_e_button = Button(print_frame, text="Adjust Extruder", width=int(b_width), command=toggleE).pack()
toggle_z_button = Button(print_frame, text="Adjust Z", width=int(b_width), command=toggleZ).pack()

# <1><2:0:10:1:0:0:0:1:0>
def updateController():
	root.update()


if __name__ == "__main__":
	while True:	
		try:
			root.update()
		except KeyboardInterrupt:
			break
