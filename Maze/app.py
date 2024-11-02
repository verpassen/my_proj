#!/urs/bin/env python 
#-*- coding: utf:8 -*-

from tkinter import *
from tkinter import messagebox, filedialog

class app():
	def __init__(self,master):
		self.frames = Frame(master)
		master.geometry('500x500')
		self.frames.pack()
		self.__min_x, self.__max_x = 10, 300
		self.__min_y, self.__max_y = 10, 300
		self.n = 10 
		self.para_set()
		self.create_widget()
		self.check_maze()
		
	def create_widget(self):
		B1 = Button(self.frames,text='Cancel')
		B1.grid(row=1,column=2)		
		B2 = Button(self.frames,text='Ok')
		B2.grid(row=1,column=1)
		B1.bind("<Button-1>",self.clr_screen)
		B3 = Button(self.frames,text = 'output')
		B3.grid(row=2,column=4)
		self.W1 = Canvas(self.frames,bg='white',width=350,height=350)
		self.W1.grid()

 		#draw the frame line
		for i in range(11):
			self.W1.create_line( self.__min_x, self.__min_y + i*self.step_y, self.__max_x, self.__min_y + i*self.step_y)#row
			self.W1.create_line( self.__min_x + i*self.step_x, self.__min_y, self.__min_x + i*self.step_x, self.__max_y)#column
		
		self.W1.bind("<Button-1>",self.mouse_click)
		self.W1.bind("<Double-1>",self.clr_screen)
	def mouse_click(self,event):
		# the position that user click might not accurate
		# we have to caculate the closest blank based on the coord. of mouse click 
		tmp_x = event.x - self.step_x/2
		tmp_y = event.y - self.step_y/2
		seq_x ,seq_y= self.seq(self.n,self.__min_x,self.step_x) , self.seq(self.n,self.__min_y,self.step_y)
		select_x,select_y = self.close_x(seq_x,tmp_x), self.close_x(seq_y,tmp_y)
		select_xn , select_yn = (select_x- self.__min_x)/self.step_x + 1,(select_y- self.__min_y)/self.step_y + 1  
		#fill the rectangle 
		self.obj_rec = self.W1.create_rectangle(select_x, select_y, select_x + self.step_x, select_y + self.step_y,fill='blue')		
		
		self.Maze_pos.append([select_xn,select_yn])
		
	def para_set(self):
		print('into para setting')	
		self.Maze_pos = []  # record position by list 

		self.step_x, self.step_y = (self.__max_x - self.__min_x)/self.n, (self.__max_y - self.__min_y)/self.n
		# set the start and exit of the maze
		self.pos_in = [1,3]
		self.pos_out = [9,10]
		
	def clr_screen(self,event):
		#clean the canvas
		print('into clear screen')
		self.W1.delete(self.obj_rec)

	def seq(self,n,min_i,step):
		#create a sequence based on the given range and step
		ans = [min_i + step*k for k in range(n)]
		return ans

	def close_x(self,s,x):
		# to find the closest point on the grid
		# s is the given sequence
		# x is the given number
		if x<s[0]:
			ans = s[0]
			print('given x is less than 1st no.')
		elif x > s[-1]:
			ans = s[-1]
			print('given x is larger than last no.')
		else:
			for k in range(len(s)):
				if x - s[k] < 0:
					if abs(x-s[k]) > abs(x-s[k-1]):
						ans = s[k-1]
						break
					else:
						ans = s[k]
						break
		return ans
		
	def fill_col(self,x,y):
		tmp_x, tmp_y =  self.__min_x + (x-1)*self.step_x , self.__min_y + (y-1)* self.step_y
		self.W1.create_rectangle(tmp_x,tmp_y,tmp_x+self.step_x,tmp_y+self.step_y,fill='green')		
	
	def fill_text(self,x,y,msg):
		tmp_x, tmp_y =  self.__min_x + (x-0.5)*self.step_x , self.__min_y + (y-0.5)* self.step_y
		self.W1.create_text(tmp_x,tmp_y,text=msg)
	
	def check_maze(self):
		print('into check maze')
		self.fill_col(self.pos_in[0],self.pos_in[1])
		self.fill_col(self.pos_out[0],self.pos_out[1])
		self.fill_text(self.pos_in[0],self.pos_in[1],'Start')
		self.fill_text(self.pos_out[0],self.pos_out[1],'Exit')

root = Tk()
b1 = app(root)
root.mainloop()
