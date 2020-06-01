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

	def __getitem__(self, index):
		return self.cell_list[index]

	def connect_cells(self):
		for row in self.cell_list:
			for cell in row:
				cell.connect_with_neighbors(self)

	def reset(self):
		self.cell_list = [ [ Cell(self.display, (x, y), grid_size=self.size) for x in range(self.size) ] for y in range(self.size) ]
		self.connect_cells()

	def draw(self):
		for r in self.cell_list:
			for cell in r:
				cell.draw()

def main():
	pygame.init()
	DISPLAY = pygame.display.set_mode((600, 600))
	pygame.display.set_caption('Grid Test')

	grid = Grid(DISPLAY, 30)

	cell = grid[5][5]
	cell2 = grid[5][6]

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
			
		update_display()
	checking = False
	pygame.quit()

if __name__ == '__main__':
	main()