INIT_BITS = 0b0000000000000000
WALL_BITS = 0b0000000000001111
VISITED_BITS = 0b0000000011110000
SOLUTION_BITS = 0b0000111100000000


class test():
	def __init__(self):
		self.a = INIT_BITS
		self.b = INIT_BITS
		self.c = INIT_BITS
		self.Q = []
		self.maze_array = [INIT_BITS]*10
	def explore_start(self):
		self.a |= VISITED_BITS
		self.maze_array[0]=self.a

	def visit_neighbor(self,from_cell,to_cell):
		print('from %d to %d' % (from_cell,to_cell))
		self.b |= VISITED_BITS
	def check_visited(self,cell):
		if cell & VISITED_BITS:
			print('visited')
		else:
			print('not visited')


kk = test()
print('a=',kk.a,'b=',kk.b)
kk.explore_start()
kk.visit_neighbor(kk.a,kk.b)
kk.check_visited(kk.b)
kk.check_visited(kk.a)

