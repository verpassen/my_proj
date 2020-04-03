#!/urs/bin/env python 
#-*- coding: utf:8 -*-

from tkinter import *
from tkinter import messagebox, filedialog

class app():
	def __init__(self,master):
		self.frames = Frame(master)
		master.geometry('500x500')
		self.frames.pack()
		self.create_widget()

	def create_widget(self):
		B1 = Button(self.frames,text='Cancel')
		B1.grid(row=1,column=1)		
		B2 = Button(self.frames,text='Ok')
		B2.grid(row=1,column=2)
		W1 = Canvas(self.frames,bg='white',width=350,height=350)
		W1.grid()
		#canvas draw the board
		self.max_x, self.min_x, self.min_y, self.max_y = 10,300,10,300
		n = 10 
		step_x,step_y = (max_x-min_x)/n,(max_y-min_y)/n
 		#draw the frame line
		for i in range(11):
			W1.create_line(min_x,min_y+i*step_y,max_x,min_y+i*step_y)#row
			W1.create_line(min_x+i*step_x,min_y,min_x+i*step_x,max_y)#column
		W1.bind("<Button-1>",self.mouse_click)

	def mouse_click(self,event):
		select_x = max(0,min(,self.max_x))
		create_rectangle(select_x,select_x+step_x,select_y,select_y+step_x)		


root = Tk()
b1 = app(root)
root.mainloop()
