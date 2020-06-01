from wall import *


def is_valid_position(position, maximum, minimum=0):
	return (minimum <= position[0] and minimum <= position[1]) and (maximum >= position[0] and maximum >= position[1])

def remove_wall_between(cell1, cell2):
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

class Cell:

	def __init__(self, display, position, color=(255, 255, 255), side=None, grid_size=None):
		self.display = display
		self.grid_size = 50 if grid_size is None else grid_size
		display_size = min(self.display.get_size())
		self.side = display_size/self.grid_size if side is None else side
		self.wtcr = 100
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
		self.in_path = False
		self.is_branch = False
		factor = 10 if self.grid_size < 50 else 0
		self.latency = 1 / (factor ** (self.grid_size/10)) if factor > 0  else 0

	def connect_with_neighbors(self, grid):
		for dirc in DIRECTIONS:
			x, y = apply_transform(self.position, dirc)
			if is_valid_position((x, y), grid.size - 1):
				n = grid[y][x]
				self.add_neighbor(n)

	def determine_color(self):
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
		return [n for n, w in zip(self._neighbors, self.walls) if w.is_open() and (not n.in_path)]	

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
			ws.append(w)
		return [c] + ws

	def update(self, latency=0):
		things_to_update = self.draw()
		for rect in things_to_update:
			pygame.display.update(rect)
		time.sleep(latency)

	def add_neighbor(self, neighbor):
		direction = determine_direction(self.position, neighbor.position)
		if direction == 0:
			merge_walls(neighbor.lower_wall, self.upper_wall)
		elif direction == 1:
			merge_walls(neighbor.right_wall, self.left_wall)
		elif direction == 2:
			merge_walls(neighbor.upper_wall, self.lower_wall)
		elif direction == 3:
			merge_walls(neighbor.left_wall, self.right_wall)
		else:
			raise Exception(f"The Cell at the position {neighbor.position} can not be a neighbor of the Cell at {self.position}")

		self._neighbors[direction] = neighbor

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
		
		self.update(self.latency)

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