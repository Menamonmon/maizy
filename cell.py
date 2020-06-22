from wall import *


def is_valid_position(position, maximum, minimum=0):
	return (minimum <= position[0] and minimum <= position[1]) and (maximum >= position[0] and maximum >= position[1])

def remove_wall_between(cell1, cell2, update=False):
	p1 = cell1.position
	p2 = cell2.position
	direction = determine_direction(p1, p2)
	if direction == 0:
		cell1.upper_wall.hide()
	elif direction == 1:
		cell1.left_wall.hide()
	elif direction == 2:
		cell1.lower_wall.hide()
	elif direction == 3:
		cell1.right_wall.hide()

	if update:
		cell1.update()
		cell2.update()

def are_cells_connected(cell1, cell2):
	direction = determine_direction(cell1.position, cell2.position)
	if direction == 0:
		w1, w2 = cell1.upper_wall, cell2.lower_wall
	elif direction == 1:
		w1, w2 = cell1.left_wall, cell2.right_wall
	elif direction == 2:
		w1, w2 = cell1.lower_wall, cell2.upper_wall
	elif direction == 3:
		w1, w2 = cell1.right_wall, cell2.left_wall
	else:
		raise Exception(f'The cells at the positions {cell1.position} and {cell2.position} are not adjacent')
	
	wall1_match = w1.friend == w2
	wall2_match = w2.friend == w1
	if wall1_match != wall2_match:
		raise Exception(f'The walls are not properly connected for the cells at {cell1.position} and {cell2.position}.')
	else:
		return wall1_match
	
def cells_in_same_sets(c1, c2):
	return c1.position in c2.cells_set and c2 in c1.cells_set

def join_cell_sets(c1, c2):
	new_set = c1.cells_set.union(c2.cells_set)
	# print('The new set is ', new_set)
	for cell in c1.cells_set:
		cell.cells_set = new_set
	for cell in c2.cells_set:
		cell.cells_set = new_set
	# c1.cells_set, c2.cells_set = new_set, new_set
	# for cell in new_set:
	# 	cell.cells_set = new_set

class Cell:

	def __init__(self, display, position, color=(255, 255, 255), side=None, grid_size=None):
		self.display = display
		self.grid_size = 50 if grid_size is None else grid_size
		display_size = min(self.display.get_size())
		self.side = display_size/self.grid_size if side is None else side
		self.wtcr = 10
		self.position = position
		self.color = color 
		self.original_color = self.color
		self.upper_wall = Wall(self.display, self.PxlPosition, width=self.unit, height=self.side, parent=self)
		self.lower_wall = Wall(self.display, (self.PxlPosition[0], self.PxlPosition[1] + (self.unit * (self.wtcr - 1))), width=self.unit, height=self.side, parent=self)
		self.right_wall = Wall(self.display, (self.PxlPosition[0] + (self.unit * (self.wtcr - 1)), self.PxlPosition[1]), width=self.unit, height=self.side, horizontal=0, parent=self)
		self.left_wall = Wall(self.display, self.PxlPosition, width=self.unit, height=self.side, horizontal=0, parent=self)
		self._neighbors = [None, None, None, None]
		self.visited = False
		self.visited_twice = False
		self.is_current_cell = False
		self.used_in_path = False
		self.part_of_path = False
		self.is_branch = False
		self.cells_set = {self}

	def connect_with_neighbors(self, grid):
		comb_walls_list = []
		for dirc in DIRECTIONS:
			x, y = apply_transform(self.position, dirc)
			if is_valid_position((x, y), grid.size - 1):
				n = grid[y][x]
				nn = self.add_neighbor(n, not are_cells_connected(self, n))
				if nn is not None:
					comb_walls_list.append(nn)
		return comb_walls_list

	def determine_color(self):
		if self.part_of_path:
			self.color = (232, 198, 28)
			return
		if self.used_in_path:
			self.color = (51, 44, 44)
			return 
		if self.visited:
			self.color = (3, 252, 73)
			return
		if self.visited_twice:
			self.color = (3, 206, 252)
			return
		if self.is_current_cell:
			self.color = (240, 252, 3)
			return 
		
		if self.is_branch:
			self.color = (252, 3, 44)
			return
		self.color = self.original_color

	@property
	def neighbors(self):
		return [n for n in self._neighbors if n is not None and not (n.visited or n.visited_twice)]

	@property
	def open_sides(self):
		return [n for n, w in zip(self._neighbors, self.walls) if (n is not None) and (w.is_open()) and (not n.used_in_path)]	

	@property
	def walls(self):
		return (self.upper_wall, self.left_wall, self.lower_wall, self.right_wall)
	
	@property 
	def x(self):
		return int(self.PxlPosition[0] + self.unit)

	@property 
	def y(self):
		return int(self.PxlPosition[1] + self.unit)

	@property
	def unit(self):
		return self.side/self.wtcr

	@property
	def PxlPosition(self):
		return ((self.position[0] * self.side), (self.position[1] * self.side))

	@property
	def size(self):
		return (self.unit * (self.wtcr - 2), self.unit * (self.wtcr - 2))

	def draw(self):
		self.determine_color()
		# if self.color != self.original_color:
		c = pygame.draw.rect(self.display, self.color, ((self.x, self.y), self.size))
		ws = []
		for wall in self.walls:
			w = wall.draw()
			ws += w
		return [c] + ws

	def update(self, latency=0):
		things_to_update = self.draw()
		for rect in things_to_update:
			pygame.display.update(rect)
		# for n in self.neighbors:
		# 	if n is not None:
		# 		n.update()
		time.sleep(latency)

	def add_neighbor(self, neighbor, merged_walls=True):
		direction = determine_direction(self.position, neighbor.position)
		if direction == 0:
			wall1, wall2 = neighbor.lower_wall, self.upper_wall
		elif direction == 1:
			wall1, wall2 = neighbor.right_wall, self.left_wall
		elif direction == 2:
			wall1, wall2 = neighbor.upper_wall, self.lower_wall
		elif direction == 3:
			wall1, wall2 = neighbor.left_wall, self.right_wall
		else:
			raise Exception(f"The Cell at the position {neighbor.position} can not be a neighbor of the Cell at {self.position}")

		self._neighbors[direction] = neighbor
		if merged_walls:
			return merge_walls(wall1, wall2)

	def is_touched(self):
		mpos = pygame.mouse.get_pos()
		start = self.PxlPosition
		end = (self.PxlPosition[0] + self.side, self.PxlPosition[1] + self.side)
		return (start[0] <= mpos[0] and mpos[0] <= end[0]) and (start[1] <= mpos[1] and mpos[1] <= end[1]) 

	def is_clicked(self, button=0):
		return int(self.is_touched() and pygame.mouse.get_pressed()[button])

	def choose(self, update=True):
		# self.visited = True
		if self.visited: 
			self.visited = False
			self.visited_twice = True
		else:
			if self.visited_twice:
				raise Exception(f'The cell at the position {self.position} is chosen more then twice')
			self.visited = True

	def unchoose(self):
		self.visited = False
		self.visited_twice = False
		
def main():
	pygame.init()
	DISPLAY = pygame.display.set_mode((600, 600))
	pygame.display.set_caption('Cell Test')

	cell = Cell(DISPLAY, (3, 3))
	cell2 = Cell(DISPLAY, (3, 4))
	cell.add_neighbor(cell2)

	def update_display():
		global hidden
		DISPLAY.fill((255, 255, 255))

		if cell.is_clicked():
			cell.lower_wall.hide()
		if cell2.is_clicked():
			cell2.upper_wall.hide()

		if cell.is_clicked(2):
			cell.lower_wall.show()
		if cell2.is_clicked(2):
			cell2.upper_wall.show()

		cell.draw()
		cell2.draw()
		pygame.display.update()

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		update_display()
		
	pygame.quit()

if __name__ == '__main__':
	main()