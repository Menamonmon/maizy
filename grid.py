from cell import *

class Grid:

	def __init__(self, display, size=50):
		if size > 300:
			raise Exception('The size of the maze is too big')
		elif size <= 0:
			raise Exception('The size of the maze cannot be zero/negative number')
		self.display = display
		self.size = size
		self.min_width = min(self.display.get_size())
		self.cell_side = self.min_width/self.size
		self.cell_list = [ [ Cell(self.display, (x, y), grid_size=self.size) for x in range(self.size) ] for y in range(self.size) ]
		# self.cell_list = [ [ Cell(self.display, (c, r), grid_size=self.size) for c in range(self.size) ] for r in range(self.size) ]
		self.connect_cells()

	def __iter__(self):
		for row in self.cell_list:
			yield row

	def __len__(self):
		return len(self.cell_list)

	def __getitem__(self, index):
		return self.cell_list[index]

	def connect_cells(self):
		self.walls = []
		for row in self.cell_list:
			for cell in row:
				self.walls += cell.connect_with_neighbors(self)

	def	walls_for_cell(self, cell):
		return [wall for wall in self.walls if cell in wall.cells]

	def reset(self):
		self.cell_list = [ [ Cell(self.display, (x, y), grid_size=self.size) for x in range(self.size) ] for y in range(self.size) ]
		self.connect_cells()

	def draw(self):
		for r in self.cell_list:
			for cell in r:
				cell.draw()

class SubGrid:

	def __init__(self, cell_list : list, horizontal=1):
		self.cell_list = cell_list
		self.horizontal = horizontal
		if not self.horizontal:
			s1x, s1y = 0, 0
			e1x, e1y = int(len(cell_list[0])/2), len(cell_list)
			s2x, s2y = e1x, 0
			e2x, e2y = len(cell_list[0]), len(cell_list)
		else:
			s1x, s1y = 0, 0
			e1y, e1x = int(len(cell_list[0])/2), len(cell_list)
			s2y, s2x = e1y, 0
			e2y, e2x = len(cell_list[0]), len(cell_list)

			
		# s1*, e1* represents the start and the end of the first half of the divided list
		# s2*, e2* represents the start and the end of the second half of the divided list

		try:
			self.sublists = [
			[cell_list[y][s1x:e1x] for y in range(s1y, e1y)],
			[cell_list[y][s2x:e2x] for y in range(s2y, e2y)]
			]
		except IndexError:
			raise Exception(f'Start 1 is ({s1x}, {s1y}) end 1 ({e1x}, {e1y}) start 2 ({s2x}, {s2y}) end 2 ({e2x}, {e2y})')
		
		self.hidden = False

		# row = len(self.sublists[0][0])
		# col = len(self.sublists[0])
		

		self.generate_maze()

	def open_wall(self):
		if not self.hidden:
			if len(self.sublists[0]) == 0:
				return
			hide_wall(self.sublists[0], 0)
			self.hidden = True
		else:
			raise Exception(f'The SubGrid from the cell at {self.cell_list[0][0].position} to the cell at {self.cell_list[-1][-1].position} has already hidden a wall')


	# def foo(self):
	# 	for i, sub in enumerate(self.sublists):
	# 		for row in sub:
	# 			for cell in row:
	# 				if i:
	# 					cell.choose()
	# 				else:
	# 					cell.choose()
	# 					cell.choose()

	# 				# cell.update()
	
	def generate_maze(self):
		self.open_wall()
		new_girds = [SubGrid(sub, not self.horizontal) for sub in self.sublists]
		[g.open_wall() for g in new_girds]

		return new_girds		

def hide_wall(cell_list, direction=0):
	y, x = len(cell_list), len(cell_list[0])
	
	if y <= x: # checks whether the cells grid is horizontal or vertical
		if not direction:
			wall_list = [cell.lower_wall for cell in cell_list[-1]]
		else:
			wall_list = [cell.upper_wall for cell in cell_list[0]]
	
	else:
		if not direction:
			wall_list = [row[-1].right_wall for row in cell_list]
		else:
			wall_list = [row[0].left_wall for row in cell_list]

	random_wall = rd.choice(wall_list)
	random_wall.hide()
	random_wall.parent.update()
	random_wall.friend.parent.update()
	


def main():
	pygame.init()
	DISPLAY = pygame.display.set_mode((600, 600))
	pygame.display.set_caption('Grid Test')

	grid = Grid(DISPLAY, 30)

	cell = grid[5][5]
	cell2 = grid[5][6]

	# sgrid = SubGrid(grid.cell_list)

	# sgrid.foo()
	# grid.make_cell_sets()

	def update_display():
		DISPLAY.fill((255, 255, 255))
		grid.draw()
		pygame.display.update()
		if cell.is_clicked():
			cell.lower_wall.hide()
		if cell2.is_clicked():
			cell2.upper_wall.hide()

		if cell.is_clicked(2):
			cell.lower_wall.show()
		if cell2.is_clicked(2):
			cell2.upper_wall.show()


	running = True
	while running:

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if event.type == pygame.KEYDOWN:
				print(cells_in_same_sets(cell, cell2))
				new_set = cell.cells_set.union(cell2.cells_set)
				print('The new set is ', new_set)
				cell.cells_set, cell2.cells_set = new_set, new_set
				cell.update()
				cell.update()
				print(cells_in_same_sets(cell, cell2))
			
		update_display()
	checking = False
	pygame.quit()

if __name__ == '__main__':
	main()