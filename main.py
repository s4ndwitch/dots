import pygame
import sys

FIRST = 0
SECOND = 1


class Game(object):
	"""Класс, отвечающий за основной игровой процесс"""
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
		self.dot_color_1 = pygame.Color("red")  # Цвет точки одного игрока
		self.dot_color_2 = pygame.Color("blue")  # Цвет точки другого игрока
		self.field = [[None for _ in range(size[0])] for _ in range(size[1])]  # Клеточное поле, собственно
		self.move = FIRST

	def draw(self):
		"""Перерисовка всех pygame объектов; клетки"""
		for i in range(0, self.size[0]):
			pygame.draw.line(
				self.surface, self.cell_color, [i * self.scale, 0], [i * self.scale, self.size[1] * self.scale])
		for i in range(0, self.size[1]):
			pygame.draw.line(
				self.surface, self.cell_color, [0, i * self.scale], [self.size[0] * self.scale, i * self.scale])

		for i in range(len(self.field)):
			for j in range(len(self.field[0])):
				if self.field[i][j]:
					self.field[i][j].draw(self.surface)

	def handle_mouse_click(self, x: int, y: int):
		"""Обработка нажатия на кнопку мыши: преобразуются координаты, заполняется игровое поле"""
		x_true, y_true = x // self.scale, y // self.scale
		if x_true == 0 or x_true == 19 or y_true == 0 or y_true == 19:
			# Дополнительная проверка: не будем ставить в самый край листочка
			return
		if self.move == FIRST:
			if not self.field[x_true][y_true]:
				# Если клетка уже не занята!
				self.field[x_true][y_true] = Dot(x_true, y_true, self.scale // 4, self.dot_color_1, self.scale)
		else:
			if not self.field[x_true][y_true]:
				self.field[x_true][y_true] = Dot(x_true, y_true, self.scale // 4, self.dot_color_2, self.scale)
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
				from pprint import pprint
				pprint(self.field)
				pygame.quit()
				sys.exit()
			elif event.type == pygame.MOUSEBUTTONDOWN:
				self.handle_mouse_click(*event.pos)

	def run(self):
		"""Игровой процесс - обрабатываем события, обновляем, отрисовываем..."""
		while self.is_accessible_field():
			self.check_points()
			self.surface.fill(self.screen_color)
			self.handle_events()
			self.draw()
			pygame.display.update()
			self.clock.tick(self.fps)

	def is_accessible_field(self) -> bool:
		"""Проверяем, есть ли свободное место для клеток на поле"""
		for array in self.field[1:self.size[0] - 1]:
			if not all(array[1:self.size[1] - 1]):
				# Мы не учитываем самые крайние узлы - они не заполняются!
				return True
		return False

	def check_points(self):
		"""Проверяем, не окружены ли какие-нибудь точки"""
		for i in range(len(self.field)):
			for j in range(len(self.field[0])):
				# Algorithm
				pass

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

	def draw(self, surface):
		"""Отрисовка"""
		pygame.draw.circle(surface, self.color, (self.x * self.scale, self.y * self.scale), self.radius)


if __name__ == '__main__':
	app = Game("Dots", 600, 600, 50)
	app.run()
