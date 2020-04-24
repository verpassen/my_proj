#define a maze by list
#5 means the wall 
#start postion is left up most pos.
#target /gaol is right bottom most pos.
#aim : to find the way from the start pos to goal by DFS & BFS
import sys
#kp_maze =  [[0,0,5,5,5,5],[5,0,5,0,0,5],[5,0,0,0,5,5],[5,0,5,0,5,5],[5,0,5,0,0,0],[5,5,5,5,5,0]]
#kp_maze =  [[0,5,5,5,5,5],[0,0,5,0,0,5],[5,0,5,0,5,5],[5,0,5,0,5,5],[5,0,0,0,5,5],[5,5,5,0,0,0]]
#kp_maze =  [[0,0,5,0,0,0],[5,0,5,0,5,0],[5,0,5,0,5,0],[5,0,0,0,5,0],[5,0,5,5,5,0],[5,0,0,0,5,0]]
kp_maze =  [[5,5,5,5,0,0],[5,0,0,0,5,5],[5,0,5,0,0,5],[5,0,0,5,0,5],[5,5,5,0,0,0],[0,0,5,0,5,0]]

# pending feature 
#============================================#
# expand the size of the maze 
# what would happen if there is no way out ?
# generating the maze automatedly
#
#============================================#

'''
class create_maze():
	def __init__(self):
		pass
	def choose_maze(self,opt):
		if opt == 1:
			return [[0,0,5,5,5,5],[5,0,5,0,0,5],[5,0,0,0,5,5],[5,0,5,0,5,5],[5,0,5,0,0,0],[5,5,5,5,5,0]]
		elif opt==2 :
			return  [[0,5,5,5,5,5],[0,0,5,0,0,5],[5,0,5,0,5,5],[5,0,5,0,5,5],[5,0,0,0,5,5],[5,5,5,0,0,0]]
		elif opt==3 :
			return [[0,5,5,5,5,5],[0,0,5,0,0,5],[5,0,5,0,5,5],[5,0,5,0,5,5],[5,0,0,0,5,5],[5,5,5,0,0,0]]
		else:
			pass
'''

direction = {'W':(-1,0),'S':(0,1),'E':(1,0),'N':(0,-1)}
Dir = ['W','S','E','N']
DEFAULT_CELL = [0,0] # (visited,direction)
start_pos = 20
target_pos = 35

class solve_maze():
	def __init__(self):
		self.w_maze = 6
		self.h_maze = 6
		total_cells = self.w_maze * self.h_maze
		self.maze_array = [DEFAULT_CELL]*total_cells
		self.curr_pos = 0
		self.step_n = 0 
	def dfs_solver(self,maze,start_pos,target_pos):
		self.Que = []
		self.curr_pos = start_pos
		self.Que.append(self.curr_pos)
		self.maze_array[self.curr_pos] = [1,0]
		for kk in range(50):
			if not self.check_if_exit(self.curr_pos):		
		#while self.check_if_exit() == 0:
				self.cell_neighbor(self.curr_pos)
			self.show_state()

	def solution_array(self):
		pass
	
	def cell_neighbor(self,cell):
		curr_x , curr_y = self.cell_x_y(cell)
		ind = 0
		for i in Dir:
			new_x = curr_x + direction[i][0]
			new_y = curr_y + direction[i][1]
			print((curr_x,curr_y),'->',(new_x,new_y))
			if (new_x >=0) & (new_x < self.w_maze):
				if (new_y >=0 ) & (new_y< self.h_maze):		
					new_cell = self.x_y_cell(new_x,new_y)
					if not self.visited_cell(new_cell):
						#print('new cell is ', (new_cell,new_x,new_y))	
						#print('new cell value is ' ,kp_maze[new_x][new_y])		
						if kp_maze[new_x][new_y] == 0: # there is not a wall
							self.Que.append(new_cell)	
							self.step_n += 1
							ind = 1						
							self.go_to_cell(cell,new_cell)	
							
		if 	ind ==0 :
			# stack is empty
			print('there is no way to go')
			print('from %d to %d' % (cell,self.Que[-1]))
			self.Que.pop(-1)			
			self.go_to_cell(cell,self.Que[-1])	
			

	def cell_x_y(self,cell): #confirmed
		y = cell % self.w_maze
		x = cell // self.w_maze
		return x,y
	def x_y_cell(self,x,y): #confirmed
		return 6*x+y

	def visited_cell(self,cell):
		if self.maze_array[cell][0] == 1: #visited
			return 1
		else:
			return 0
	def go_to_cell(self,from_cell,to_cell):
		print('========')
		print('into go_to_cell function')
		print('go to cell %d' % (to_cell))
		self.maze_array[to_cell] = [1,0]
		if to_cell - from_cell == 1:
			self.maze_array[from_cell] = [1,Dir[2]]
		elif to_cell-from_cell == 6:
			self.maze_array[from_cell] = [1,Dir[1]]
		elif to_cell-from_cell == -6:
			self.maze_array[from_cell] = [1,Dir[3]]
		elif to_cell-from_cell == -1:
			self.maze_array[from_cell] = [1,Dir[0]]
		else:
			print('something wrong!')
		self.curr_pos = to_cell

	def show_state(self):
		print('current pos',self.curr_pos)
		print('stack',self.Que)
	
	def check_if_exit(self,cell):
		print('into check if exit')
		if cell == target_pos:
			print('Congradulation!')
			self.solution_array
			sys.exit()
		else:
			print('Current pos: %d' % (self.curr_pos))
			print('keep going!')
			return 0
		

def main():
	current_maze = solve_maze()	 
	current_maze.dfs_solver(kp_maze,start_pos,target_pos)

	
if __name__ == '__main__':
	main()
