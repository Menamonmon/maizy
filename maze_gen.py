from grid import *

class MazeGeneration:

	def __init__(self):
		pygame.init()
		self.DISPLAY = pygame.display.set_mode((300, 300))
		pygame.display.set_caption('Grid Test')

		self.grid = Grid(self.DISPLAY, 0)

		self.checking = True
		self._start_cell = None
		self._end_cell = None
		self.choosing_start = False
		self.choosing_end = False
		self.algo_started = False
		self.start_cell = self.grid[0][0]
		self.end_cell = self.grid[-1][-1]
		self.clicking_thread = Thread(target=self.check_cells)
		self.clicking_thread.start()
		self.fps = 0

	@property
	def start_cell(self):
		return self._start_cell
		
	@start_cell.setter
	def start_cell(self, cell):
		if self._start_cell is not None:
			self.start_cell.is_start = False
		cell.is_start = True
		self._start_cell = cell
	
	@property
	def end_cell(self):
		return self._end_cell
		
	@end_cell.setter
	def end_cell(self, cell):
		if self._end_cell is not None:
			self.end_cell.is_end = False
		cell.is_end = True
		self._end_cell = cell

	def reset(self):
		self.grid.reset()
		self.start_cell = self.grid[0][0]
		self.end_cell = self.grid[-1][-1]
		self.clicking_thread = Thread(target=self.check_cells)
		self.clicking_thread.start()

	def check_cells(self, cell_list=None):
		if cell_list is None:
			cell_list = self.grid.cell_list
		while self.checking and not self.algo_started:
			for row in cell_list:
				for cell in row:
					if cell.is_clicked():
						if self.choosing_start:
							self.start_cell = cell
						elif self.choosing_end:
							self.end_cell = cell

	def update_display(self):
		# self.DISPLAY.fill((255, 255, 255))
		self.grid.draw()
		pygame.display.update()

	def dfs(self):
		self.algo_started = True
		self.path = []
		self.search(self.start_cell)
		self.algo_started = False
	
	def search(self, current_cell):
		current_neighbors = current_cell.neighbors
		for n in current_neighbors:
			n.is_branch = True
		while len(current_cell.neighbors) > 0: # while the current cell has any unvisted neighbor cells
			random_neighbor = rd.choice(current_cell.neighbors)
			remove_wall_between(current_cell, random_neighbor)
			current_cell.is_current_cell = False
			current_cell = random_neighbor
			current_cell.choose()
			current_cell.is_current_cell = True
			self.path.append(current_cell.position)
			self.search(current_cell)
			

	def recursive_backtracking(self):
		self.algo_started = True
		stack = []
		self.fps = 0
		current_cell = self.start_cell
		current_cell.choose()
		stack.append(current_cell)
		while True:
			

			current_neighbors = current_cell.neighbors
			if len(current_neighbors) > 0:
				random_neighbor = rd.choice(current_neighbors)
				remove_wall_between(current_cell, random_neighbor)
				current_cell.is_current_cell = False 
				current_cell = random_neighbor
				current_cell.is_current_cell = True
				current_cell.choose()
				stack.append(current_cell)
			else:
				current_cell.is_current_cell = False
				current_cell = stack.pop()
				current_cell.is_current_cell = True
				current_cell.choose()

			if current_cell == self.start_cell:
				print('Maze is done')
				self.algo_started = False
				break

	def trace_solution(self):
		solution = []
		current_cell = self.start_cell
		depth = 0
		while current_cell != self.end_cell:
			if depth > (self.grid.size ** 4):
				print('This maze is unsolveable')
				return []
			solution.append(current_cell.position)
			open_sides = current_cell.open_sides
			if len(open_sides):
				current_cell = rd.choice(current_cell.open_sides)
				current_cell.in_path = True
				solution.append(current_cell.position)
			else:
				solution.pop()
			# depth += 1
		print(solution)
		return solution

	def mainloop(self):
		running = True
		while running:

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.checking = False
					running = False

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_s:
						self.choosing_start = True
					elif event.key == pygame.K_e:
						self.choosing_end = True
					elif event.key == pygame.K_RETURN:
						self.recursive_backtracking()
					elif event.key == pygame.K_r:
						self.reset()
					elif event.key == pygame.K_SPACE:
						remove_wall_between(self.grid[0][0], self.grid[1][0])
					elif event.key == pygame.K_p:
						print(self.trace_solution())
					elif event.key == pygame.K_d:
						self.dfs()
			
				if event.type == pygame.KEYUP:
					if event.key == pygame.K_s:
						self.choosing_start = False
					elif event.key == pygame.K_e:
						self.choosing_end = False
				
			self.update_display()
		pygame.quit()


def main():
	app = MazeGeneration()
	app.mainloop()

if __name__ == "__main__":
	main()