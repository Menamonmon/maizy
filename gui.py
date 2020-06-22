import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from maze_gen import *

class GUI(tk.Frame):

	def __init__(self, master, app, mode='gen', **kwargs):
		self.master = master
		super().__init__(self.master, **kwargs)
		self.master.resizable(0, 0)
		self.app = app
		self.mode = mode
		self.initialize()
		self.show_slowly = tk.IntVar()
		self.slow_motion_check = tk.Checkbutton(self.master, text='Show Slowly', variable=self.show_slowly)
		self.slow_motion_check.grid()
		
	def initialize(self):
		if self.mode == 'gen': 
			self._gen_init()
		elif self.mode == 'solve':
			self._solve_init()
		else:
			raise Exception(f'Invliad mode for the GUI {self.mode}')    

	def _gen_init(self):
		self.master.title("Generation")
		self.create_radios()
		self.gen_btn = ttk.Button(self.master, text="Generate Maze", command=self.generate)
		self.gen_btn.grid(row=len(list(self.app.GENERATORS.keys()))+1, column=2)

	def _solve_init(self):
		self.master.title('Solving The Maze')
		self.create_radios()
		self.solve_btn = ttk.Button(self.master, text='Solve', command=self.solve)
		self.solve_btn.grid(row=len(list(self.app.SOLVERS.keys()))-1, column=2)
		self.reset_btn = ttk.Button(self.master, text='Reset', command=self.reset)
		self.reset_btn.grid(row=len(list(self.app.SOLVERS.keys())), column=2)
		if self.app.solution_is_visible:
			messagebox.showinfo("Solution Ready", "The solution is shown in yellow and the cells used to make are shown in black.")

	@property
	def chosen_algo(self):
		i = self.var.get()
		for radio in self.radios:
			if i == radio['value']:
				s = self.app.GENERATORS.keys() if self.mode == 'gen' else self.app.SOLVERS.keys()
				return list(s)[i]

	def create_radios(self, **kwargs):
		self.radios = []
		title = "Algorithms for generation:" if self.mode == 'gen' else 'Algorithms for solving the maze:'
		tk.Label(self.master, text=title).grid(row=0, column=1, sticky=tk.E)
		self.var = tk.IntVar()
		keys = self.app.GENERATORS.keys() if self.mode == 'gen' else self.app.SOLVERS.keys()
		for row, algo in enumerate(keys, start=1):
			formatted = algo.capitalize()
			rd = tk.Radiobutton(self.master, value=row-1, variable=self.var)
			rd.grid(row=row, column=0, sticky=tk.W)
			self.radios.append(rd)
			tk.Label(self.master, text=formatted, **kwargs).grid(row=row, column=1, sticky=tk.W)

	def generate(self, *args):
		gen_algo = self.chosen_algo
		if gen_algo not in self.app.GENERATORS:
			messagebox.showwarning("No Gen. Algo.", "Please choose one of the generation algorithms before you click 'Generate Maze'.")
			return

		if gen_algo == 'depth first search':
			if self.app.grid.size > self.app.dfs_limit:
				messagebox.showinfo("Invalid Size for DFS", f"Please change the size of your grid because the DFS algorithm can only handle grids that are {self.app.dfs_limit} blocks or less in size.")
				return

		self.master.destroy()
		self.app.GENERATORS[gen_algo](self.app, self.show_slowly.get())

	def solve(self, *args):
		if self.app.solution_is_visible:
			messagebox.showwarning("Maze already solved", "The generated maze is already solved. You can press the 'Reset' button to generate and solve another one.")
			return 

		gen_algo = self.chosen_algo
		if gen_algo not in self.app.SOLVERS:
			messagebox.showwarning("No Solving Algo.", "Please choose one of the solving algorithms before you click 'Sovle'.")
			return

		self.master.destroy()
		self.app.SOLVERS[gen_algo](self.app, self.show_slowly.get())


	def reset(self):
		self.master.destroy()
		self.app.reset()


class SizeGUI(tk.Frame):

	def __init__(self, master, int_var):
		self.master = master
		self.int_var = int_var
		ttk.Label(self.master, text='Please Type the size of the grid that you want.\nIt cannot be more than 100. It also should be 5 or more.').pack()
		self.entry = ttk.Spinbox(self.master, from_=5, to=100)
		self.entry.insert(0, 25)
		self.entry.pack()
		self.enter_btn = ttk.Button(self.master, text='Make Grid', command=lambda x=None: self.take_size())
		self.enter_btn.pack()
		self.master.mainloop()

	def take_size(self):
		try:
			size = int(self.entry.get())
		except TypeError:
			messagebox.showwarning('Invalid Input', f'The input should not contain any letters.')
			return
		
		if size <= 4 or size > 100:
			messagebox.showwarning('Invalid Grid Size', f'The size of your grid should be between 5 and 100 not this {size}')
			return

		self.int_var.set(size)
		self.master.destroy()        