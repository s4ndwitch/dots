

import pygame
import sys


FIRST = 0
SECOND = 1
polygons = []
useless_dots = []

# Класс, отвечающий за основной игровой процесс
class Game(object):

	def __init__(self, title: str, width: int, height: int, fps: int, size=(10, 10)):

		# Инициализация звука, графики, часов, etc:
		pygame.mixer.pre_init(44100, 16, 2, 4096)
		pygame.init()
		pygame.font.init()
		self.surface = pygame.display.set_mode((width, height))
		pygame.display.set_caption(title)
		self.clock = pygame.time.Clock()
		self.fps = fps  # Частота смены кадров
		self.scale = width // size[0]  # Размер клетки
		self.size = size  # Количество клеток
		self.cell_color = pygame.Color((5, 4, 170))  # Цвет клеток (королевский синий)
		self.screen_color = pygame.Color("white")  # Цвет фона
		self.dot_color_1 = pygame.Color((255, 0, 0, 182))  # Цвет точки одного игрока
		self.dot_color_2 = pygame.Color((0, 0, 255, 182))  # Цвет точки другого игрока
		self.rect_color_1 = pygame.Color((255, 0, 0, 91))  # Цвета прямоугольников из точек
		self.rect_color_2 = pygame.Color((0, 0, 255, 91))
		self.field = [[None for _ in range(size[0] + 1)] for _ in range(size[1] + 1)]  # Клеточное поле, собственно
		self.move = FIRST

	def draw_cells(self):
		"""Перерисовка клеток"""
		for i in range(0, self.size[0]):
			pygame.draw.line(
				self.surface, self.cell_color, [i * self.scale, 0], [i * self.scale, self.size[1] * self.scale])
		for i in range(0, self.size[1]):
			pygame.draw.line(
				self.surface, self.cell_color, [0, i * self.scale], [self.size[0] * self.scale, i * self.scale])

	def draw_dots(self):
		"""Перерисовка точек"""
		for i in range(len(self.field)):
			for j in range(len(self.field[0])):
				if self.field[i][j]:
					self.surface.blit(self.field[i][j].draw(self.surface), (0, 0))
	
	def point_in_borders(self, point, borders):
		# bool result = false;
		# int j = size - 1;
		# for (int i = 0; i < size; i++) {
		# 	if ( (p[i].Y < point.Y && p[j].Y >= point.Y || p[j].Y < point.Y && p[i].Y >= point.Y) &&
		# 		(p[i].X + (point.Y - p[i].Y) / (p[j].Y - p[i].Y) * (p[j].X - p[i].X) < point.X) )
		# 		result = !result;
		# 	j = i;
		# }
		result = False
		j = len(borders) - 1
		for i in range(len(borders)):
			if ((borders[i][1] < point[1] and borders[j][1] >= point[1] or borders[j][1] < point[1] and borders[i][1] >= point[1]) and \
				(borders[i][0] + (point[1] - borders[i][1]) / (borders[j][1] - borders[i][1]) * (borders[j][0] - borders[i][0]) < point[0])):
				result = not result
			j = i
		return result

	# Обработка нажатия на кнопку мыши: преобразуются координаты, заполняется игровое поле
	def handle_mouse_click(self, x: int, y: int):

		x, y = x / self.scale, y / self.scale
		x = int(x // 1) if x % 1 < 0.5 else int(x // 1) + 1
		y = int(y // 1) if y % 1 < 0.5 else int(y // 1) + 1

		if 0 < x < self.size[0] and 0 < y < self.size[1] and not self.field[x][y]:
			self.field[x][y] = Dot(x, y, self.scale // 4, self.dot_color_1 \
			  if self.move == FIRST else self.dot_color_2, self.scale)
			area, trace = self.search_point(x, y, [])
			if area != 0:

				global polygons

				polygons += [list(map(lambda x: self.field[x[0]][x[1]], trace))]

				for_removal = []
				for i in range(len(polygons) - 1):
					if polygons and all([polygons[i][j] in polygons[-1] for j in range(len(polygons[i]))]):
						for_removal += [i]
				
				# Проверять всё поле не нужно, лишь максимально ограниченный прямоугольник.
				# Но мне лень. Так что пусть останется в заметках, что можно определить
				# максимальные границы и проверять только в них.

				for i in range(len(self.field)):
					for j in range(len(self.field[0])):
						if self.field[i][j] and self.point_in_borders((i, j), trace) and \
							self.field[i][j].get_color() != self.field[x][y].get_color():
							self.field[i][j].set_useless()

				shift = 0
				for i in for_removal:
					del polygons[i + shift]
					shift -= 1
				
		self.change_move()

	def change_move(self):
		"""Смена хода текущего игрока"""
		if self.move == FIRST:
			self.move = SECOND
		else:
			self.move = FIRST

	def handle_events(self):
		"""Соответственно, обработчик событий"""
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				self.handle_mouse_click(*event.pos)
				# self.check_points()
		

	def run(self):
		"""Игровой процесс - обрабатываем события, обновляем, отрисовываем..."""
		while self.is_accessible_field():
			self.surface.fill(self.screen_color)
			self.handle_events()
			self.draw_cells()
			self.draw_dots()
			for polygon in polygons:
				self.draw_polygon(polygon)
			pygame.display.update()
			self.clock.tick(self.fps)

	def is_accessible_field(self) -> bool:
		"""Проверяем, есть ли свободное место для клеток на поле"""
		for array in self.field[1:self.size[0] - 1]:
			if not all(array[1:self.size[1] - 1]):
				# Мы не учитываем самые крайние узлы - они не заполняются!
				return True
		return False

	def draw_polygon(self, points: list):
		"""Рисуем полигон точек"""
		color_p = points[0].get_color()
		s = self.surface.convert_alpha()
		s.fill([0, 0, 0, 0])
		if self.get_player_by_color(color_p) == FIRST:
			pygame.draw.polygon(s, self.rect_color_1, [[p.x * self.scale, p.y * self.scale] for p in points])
		else:
			pygame.draw.polygon(s, self.rect_color_2, [[p.x * self.scale, p.y * self.scale] for p in points])
		self.surface.blit(s, (0, 0))

	# i, j are for the current dot; trace starts with the searched one.
	def search_point(self, i, j, trace):

		neighbours = [(i + shift_i, j + shift_j) for shift_i in range(-1, 2) \
			for shift_j in range(-1, 2) if i + shift_i < self.size[0] \
				and j + shift_j < self.size[1] \
				and self.field[i + shift_i][j + shift_j] \
				and not (shift_i == 0 and shift_j == 0) \
				and self.field[i][j].get_color() == \
					self.field[i + shift_i][j + shift_j].get_color()\
				and (i + shift_i, j + shift_j) not in trace[1:] \
				and self.field[i + shift_i][j + shift_j].get_readiness()]

		trace, max_area, max_trace = trace + [(i, j)], 0, []
		for neighbour in neighbours:
			if (neighbour[0], neighbour[1]) == trace[0]:
				area = 0.5 * abs(sum([trace[i][0] * trace[i + 1][1] \
						for i in range(len(trace) - 1)]) + trace[-1][0] * trace[0][1] - \
						sum([trace[i + 1][0] * trace[i][1] for i in range(len(trace) - 1)]) - \
						trace[0][0] * trace[-1][1])
				if area > max_area:
					max_area = area
					max_trace = trace
			else:
				area, new_trace = self.search_point(neighbour[0], neighbour[1], trace)
				if area > max_area:
					max_area = area
					max_trace = new_trace

		return (max_area, max_trace)


	def check_points(self):

		for i in range(self.size[0] + 1):
			for j in range(self.size[1] + 1):
				if not self.field[i][j]:
					continue
				

		"""Проверяем, не окружены ли какие-нибудь точки"""
		# for i in range(len(self.field)):
		# 	for j in range(len(self.field[0])):
		# 		if self.field[i][j]:
		# 			current_player = self.get_player_by_color(self.field[i][j].get_color())
		# 			list_neighbours = [
		# 				self.field[i - 1][j], self.field[i][j + 1], self.field[i + 1][j], self.field[i][j - 1]]
		# 			count_enemies, count_friends = 0, 0
		# 			for point in list_neighbours:
		# 				if not point:
		# 					continue
		# 				if not point.get_readiness():
		# 					continue
		# 				if self.get_player_by_color(point.get_color()) != current_player:
		# 					count_enemies += 1
		# 				else:
		# 					count_friends += 1
		# 			if count_enemies == 4:
		# 				# Точка полностью окружена
		# 				self.field[i][j].set_useless()
		# 				self.draw_polygon(list_neighbours)
		# 			# print(
		# 			# 	f"Point ({i}, {j}); enemies: {count_enemies}; "
		# 			# 	f"friends: {count_friends}; is_ban: {self.field[i][j].get_readiness()}")

	def get_player_by_color(self, color_: pygame.Color):
		"""Возвращает номер игрока по цвету точки"""
		if color_ == self.dot_color_1:
			return FIRST
		return SECOND


class Dot(object):
	"""Класс той самой точки"""
	def __init__(self, x: int, y: int, r: int, color: pygame.Color, scale: int):
		self.x, self.y = x, y
		self.radius = r
		self.diameter = r * 2
		self.color = color
		self.scale = scale
		self.is_active = True  # Не в плену ли точка (в противном случае флаг равен False)

	def draw(self, surface: pygame.display):
		"""Отрисовка"""
		s = surface.convert_alpha()
		s.fill([0, 0, 0, 0])
		pygame.draw.circle(s, self.color, (self.x * self.scale, self.y * self.scale), self.radius)
		return s

	def get_color(self):
		"""Возвращаем цвет точки"""
		return self.color

	def get_readiness(self):
		"""Возвращает состояние точки (в плену, или нет)"""
		return self.is_active

	def set_useless(self):
		"""Делает точку пленной"""
		self.is_active = False


if __name__ == '__main__':
	app = Game("Dots", 600, 600, 50)
	app.run()
