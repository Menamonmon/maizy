from grid import *
from gui import *

class MazeGeneration:


	def __init__(self, disp_size=600):
		pygame.init()
		self.DISPLAY = pygame.display.set_mode((disp_size, disp_size))
		pygame.display.set_caption('Grid Test')

		self.grid_size = self.take_grid_size()
		self.grid = Grid(self.DISPLAY, self.grid_size)

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
		self.dfs_limit = 40
		self.ready = True
		self.solution_is_visible = False
		self.horizontal_div = True
		self.gui_on = False

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

	def take_grid_size(self):
		master = tk.Tk()
		int_var = tk.IntVar()
		app = SizeGUI(master, int_var)
		return int_var.get()

	def reset(self):
		self.grid.reset()
		self.start_cell = self.grid[0][0]
		self.end_cell = self.grid[-1][-1]
		self.clicking_thread = Thread(target=self.check_cells)
		self.clicking_thread.start()
		self.ready = True
		self.solution_is_visible = False

	def check_cells(self, cell_list=None):
		if cell_list is None:
			cell_list = self.grid.cell_list
		while self.checking and not self.algo_started:
			for row in cell_list:
				for cell in row:
					if cell.is_clicked():
						pass

	def update_display(self):
		# self.DISPLAY.fill((255, 255, 255))
		self.grid.draw()
		pygame.display.update()
		try:
			if hasattr(self, 'gui_on'):	
				if self.gui_on:
					self.gui.update()
		except:
			self.gui_on = False
			self.make_gui()

	def dfs(self, slow=False):
		self.algo_started = True
		self.ready = False
		self.path = []
		self.search(self.start_cell, slow)
		self.algo_started = False
	
	def search(self, current_cell, slow=False):
		current_neighbors = current_cell.neighbors
		for n in current_neighbors:
			time.sleep(.000001)
			n.is_branch = True
		while len(current_cell.neighbors) > 0: # while the current cell has any unvisted neighbor cells
			random_neighbor = rd.choice(current_cell.neighbors)
			remove_wall_between(current_cell, random_neighbor, slow)
			current_cell.is_current_cell = False
			current_cell = random_neighbor
			current_cell.choose()
			current_cell.is_current_cell = True
			self.path.append(current_cell.position)
			self.search(current_cell)
			
	
	def recursive_backtracking(self, slow=False):
		self.algo_started = True
		self.ready = False
		stack = []
		self.fps = 0
		current_cell = self.start_cell
		current_cell.choose()
		stack.append(current_cell)
		while True:
			
			current_neighbors = current_cell.neighbors
			if len(current_neighbors) > 0:
				random_neighbor = rd.choice(current_neighbors)
				remove_wall_between(current_cell, random_neighbor, slow)
				current_cell = random_neighbor
				current_cell.choose()
				stack.append(current_cell)
			else:
				current_cell = stack.pop()
				current_cell.choose()

			if current_cell == self.start_cell:
				self.algo_started = False
				break

	def prim(self, slow=False):
		self.algo_started = True
		self.ready = False
		maze_cells = []
		wall_list = []
		current_cell = self.start_cell
		maze_cells.append(current_cell)
		current_cell.choose()
		wall_list += self.grid.walls_for_cell(current_cell)
		while len(wall_list) > 0:
			random_wall = rd.choice(wall_list)
			associated_cells = [cell for cell in random_wall.cells if not cell.visited]
			if len(associated_cells) == 1:
				cells = random_wall.cells
				c1, c2 = cells[0], cells[1]
				remove_wall_between(c1, c2, slow)
				current_cell = associated_cells[0]
				maze_cells.append(current_cell)
				current_cell.choose()
				# current_cell.update()
				wall_list += self.grid.walls_for_cell(current_cell)
			wall_list.remove(random_wall)

	def kruskal(self):
		# self.grid.make_cell_sets()
		wall_list = self.grid.walls
		rd.shuffle(wall_list)
		
		for wall in wall_list:
			cell1 = wall.cells[0]
			cell2 = wall.cells[1]
			if not cells_in_same_sets(*wall.cells):
				wall.hide()
				join_cell_sets(*wall.cells)
			else:
				print("End of branch")
				
	def backtracking_solution(self, slow=False):
		solution = []
		current_cell = self.start_cell
		current_cell.used_in_path = True
		while current_cell != self.end_cell:
			open_neighbors = current_cell.open_sides
			if len(open_neighbors):
				if current_cell not in solution:
					solution.append(current_cell)
				current_cell = rd.choice(open_neighbors)
				current_cell.used_in_path = True
			else:
				current_cell = solution.pop()

			if not slow:
				current_cell.update()

		for cell in solution:
			cell.part_of_path = True
			cell.update()
		solution_positions = [cell.position for cell in solution]
		self.solution_is_visible = True
		return tuple(solution_positions), len(solution_positions)
	
	def deadend_solution(self, slow=False):
		dead_ends = []
		# making a list of dead ends
		for row in self.grid:
			for cell in row:
				if len(cell.open_sides) == 1:
					if (cell.position != self.start_cell.position and cell.position != self.end_cell.position):
						dead_ends.append(cell)
						cell.used_in_path = True
						if not slow:
							cell.update()
		
		# filling the dead ends
		for deadEnd in dead_ends:
			self.fill_dead_end(deadEnd, slow)

		solution = []
		# marking all the cells other than that path of the dead ends as part of the solution
		for row in self.grid:
			for cell in row:
				if not cell.used_in_path:
					# cell.part_of_path = True
					solution.append(cell)

		# sorting the list of the solution based on the value of the position and marking them as part of the path and updating their color
		solution = sorted(solution, key=lambda x: sum(x.position))
		for cell in solution:
			cell.part_of_path = True
			if not slow:
				cell.update()
		
		# converting the solution list from cells to their positions
		solution = [cell.position for cell in solution]
		self.solution_is_visible = True
		return solution, len(solution)

	def fill_dead_end(self, cell, slow=False):
		if len(cell.open_sides) > 1 or not len(cell.open_sides):
			return
		else:
			current_cell = cell.open_sides[0]
		while len(current_cell.open_sides) == 1 and current_cell != self.end_cell:
			if current_cell != self.start_cell:	
				current_cell.used_in_path = True
				current_cell = current_cell.open_sides[0]
				if not slow:
					current_cell.update()
			else:
				break
			
	GENERATORS = {'recursive backtracking': recursive_backtracking,
				  "prim's algorithm": prim,
				  'depth first search': dfs}

	SOLVERS = {'backtracking': backtracking_solution, 
			   'dead-end filling': deadend_solution}

	def make_gui(self):
		# if self.ready:
		if not self.gui_on:	
			self.gui_on = True
			mode = 'gen' if self.ready else 'solve'
			self.gui_master = tk.Tk()
			self.gui = GUI(self.gui_master, self, mode)

	def mainloop(self):
		running = True

		self.make_gui()
		while running:

			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					self.checking = False
					running = False
			self.update_display()
		pygame.quit()


def main():
	app = MazeGeneration()
	app.mainloop()

if __name__ == "__main__":
	main()