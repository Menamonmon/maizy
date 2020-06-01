import pygame
from threading import Thread
import time
import random as rd

COLORS = [
	(128, 0, 0),
	(0, 128, 0),
	(245, 179, 66),
	(0, 0, 0),
	(57, 81, 82),
	()
]

DIRECTIONS = [
		(0, 1),
		(1, 0),
		(0, -1),
		(-1, 0)
	]

def determine_direction(pos1, pos2):
	difference = (pos1[0] - pos2[0], pos1[1] - pos2[1])
	if difference in DIRECTIONS:
		return DIRECTIONS.index(difference)    


def apply_transform(positon, transform):
	return (positon[0] + transform[0], positon[1] + transform[1])
	

class Cover:

	def __init__(self, parent):
		self.parent = parent
		self.horizontal = self.parent.horizontal
		h = self.parent.height
		w = self.parent.width
		if not self.horizontal:
			self.height = h * ((self.wtcr - 2)/self.wtcr)
			self.width = w
		else:
			self.height = h 
			self.width = w * ((self.wtcr - 2)/self.wtcr)
		self._color = None

	@property
	def color(self):
		self.parent.parent.determine_color()
		return self.parent.parent.color

	@property
	def wtcr(self):
		return self.parent.parent.wtcr

	@property
	def x(self):
		if self.horizontal:
			return self.parent.position[0] + (self.parent.width/self.wtcr)
		return self.parent.position[0]

	@property
	def y(self):
		if not self.horizontal:
			return self.parent.position[1] + (self.parent.height/self.wtcr)
		return self.parent.position[1]

	def draw(self):
		return pygame.draw.rect(self.parent.display, self.color, ((self.x, self.y), (self.width, self.height)))


class Wall:

	def __init__(self, display, position, color=(0, 0, 0), width=10, height=40, horizontal=1, parent=None):
		self.display = display
		self.position = position
		self.color = color
		self.original_color = self.color
		self.horizontal = horizontal
		if self.horizontal:
			height, width = width, height
		   
		self.width = width 
		self.height = height 
		self._visible = True
		self.friend = None
		self.parent = parent
		self.covered = False
		self.cover = Cover(self)

	def draw(self, corners=True):
		if not self.covered or corners:
			pygame.draw.rect(self.display, self.color, (self.position, (self.width, self.height)))
		
		if self.covered:
			self.cover.draw()
			if not corners:
				return
		

	@property
	def is_border_wall(self):
		return self.friend == None
	
	@property
	def visible(self):
		return self._visible
		
	@visible.setter
	def visible(self, value):
		self._visible = value
		if not self.visible:
			if self.parent is not None:
				self.color = self.parent.color
			
		else:
			self.color = self.original_color
			
	def hide(self, cover=True, with_border_walls=False):
		if not self.is_border_wall or with_border_walls:
			if not cover:
				self.visible = False
				if not self.is_border_wall:
					self.friend.visible = False
			else:
				self.covered = True
				if not self.is_border_wall:
					self.friend.covered = True

	def show(self, with_border_walls=False):
		if not self.is_border_wall or with_border_walls:
			self.visible = True
			if not self.is_border_wall:
				self.friend.visible = True
			if self.covered:
				self.covered = False
				if not self.is_border_wall:
					self.friend.covered = False
				
	def is_open(self):
		if self.covered or (not self.visible):
			return True
		return False


def merge_walls(wall1, wall2):
	wall1.friend, wall2.friend = wall2, wall1

def main():
	pygame.init()
	DISPLAY = pygame.display.set_mode((600, 600))
	pygame.display.set_caption('Wall Test')

	wall = Wall(DISPLAY, (50, 50))

	def update_display():
		DISPLAY.fill((255, 255, 255))
		wall.draw()
		pygame.display.update()

	running = True
	while running:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_UP:
					wall.hide()
				
		update_display()
		
	pygame.quit()

if __name__ == '__main__':
	main()