import pygame
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
from pygame_widgets.toggle import Toggle

from .events import *


PINK = (255, 105, 180)
LIGHT_PINK = (255, 235, 245)
WHITE = (255, 255, 255)
GRAY = (210, 210, 210)

MAIN_X = 1050
MAIN_W = 150
MAIN_H = 42


def pink_button(window, x, y, width, height, text, font_size, on_click):
    return Button(
        window, x, y, width, height,
        text=text,
        radius=12,
        font=pygame.font.SysFont('Verdana', font_size, bold=True),
        onClick=on_click,
        inactiveColour=WHITE,
        hoverColour=LIGHT_PINK,
        pressedColour=(255, 210, 230),
        textColour=PINK,
        borderColour=PINK,
        borderColor=PINK,
        borderThickness=2,
        margin=0,
    )


def sidebar_widgets(window):
    prev_button = pink_button(
        window, 1028, 18, 28, 42, '<', 16,
        lambda: pygame.event.post(pygame.event.Event(PREVIOUS_EVENT))
    )

    label = Label(window, 'Level 0', 1060, 18, 19, width=115, height=42)

    next_button = pink_button(
        window, 1180, 18, 28, 42, '>', 16,
        lambda: pygame.event.post(pygame.event.Event(NEXT_EVENT))
    )

    moves = Label(window, 'Moves - 0', MAIN_X, 90, 18, width=MAIN_W, height=MAIN_H)

    restart = pink_button(
        window, MAIN_X, 145, MAIN_W, MAIN_H, 'Restart', 18,
        lambda: pygame.event.post(pygame.event.Event(RESTART_EVENT))
    )

    seed = Label(window, 'Seed', MAIN_X, 205, 15, width=65, height=36)

    seedbox = TextBox(
        window, MAIN_X + 75, 205, 75, 36,
        placeholderText='',
        borderColour=PINK,
        textColour=PINK,
        colour=WHITE,
        onSubmit=lambda: pygame.event.post(pygame.event.Event(RANDOM_GAME_EVENT)),
        borderThickness=2,
        radius=10,
        font=pygame.font.SysFont('Verdana', 14, bold=True),
    )

    random_game = pink_button(
        window, MAIN_X, 260, MAIN_W, MAIN_H, 'Random', 18,
        lambda: pygame.event.post(pygame.event.Event(RANDOM_GAME_EVENT))
    )

    bfs_button = pink_button(
        window, MAIN_X, 320, MAIN_W, MAIN_H, 'Solve BFS', 18,
        lambda: pygame.event.post(pygame.event.Event(SOLVE_BFS_EVENT))
    )

    astarman_button = pink_button(
        window, MAIN_X, 380, MAIN_W, MAIN_H, 'A* Manhattan', 14,
        lambda: pygame.event.post(pygame.event.Event(SOLVE_ASTARMAN_EVENT))
    )

    dijk_button = pink_button(
        window, MAIN_X, 440, MAIN_W, MAIN_H, 'Dijkstra', 14,
        lambda: pygame.event.post(pygame.event.Event(SOLVE_DIJKSTRA_EVENT))
    )

    visualizer = Label(window, 'Visualize', MAIN_X, 500, 15, width=105, height=36)

    toggle = Toggle(
        window, MAIN_X + 115, 508, 35, 20,
        handleRadius=11,
        offColour=GRAY,
        onColour=LIGHT_PINK,
        handleColour=WHITE,
    )

    paths = MultilineLabel(window, 'Solution Depth: 0\n', 64, 0, 20)
    level_clear = LevelClear(window, 'Level Clear!')

    return {
        'restart': restart,
        'random_button': random_game,
        'moves_label': moves,
        'prev_button': prev_button,
        'next_button': next_button,
        'label': label,
        'level_clear': level_clear,
        'toggle': toggle,
        'visualizer': visualizer,
        'bfs': bfs_button,
        'paths': paths,
        'seedbox': seedbox,
        'seed': seed,
        'astarman': astarman_button,
        'dijkstra': dijk_button,
    }


class Label:
    def __init__(self, window, text, x, y, font_size, transparency=False, color=PINK, width=None, height=None):
        self.x = x
        self.y = y
        self.font = pygame.font.SysFont('Verdana', font_size, bold=True)
        self.image = self.font.render(text, True, color)
        self.rect = pygame.Rect(
            x,
            y,
            width if width else self.image.get_width() + 24,
            height if height else self.image.get_height() + 18
        )
        self.window = window
        self.transparency = transparency
        self.solved = False
        self.color = color

    def set_text(self, new_text, font_size, color=PINK):
        if 'Level' in new_text:
            font_size = 19

        self.font = pygame.font.SysFont('Verdana', font_size, bold=True)
        self.image = self.font.render(new_text, True, color)
        self.color = color
        self.draw()

    def set_moves(self, new_text, font_size, color=PINK):
        self.font = pygame.font.SysFont('Verdana', font_size, bold=True)
        self.image = self.font.render(new_text, True, color)
        self.color = color
        self.rect.width = MAIN_W
        self.rect.height = MAIN_H
        self.draw()

    def draw(self):
        pygame.draw.rect(
            self.window,
            WHITE,
            self.rect,
            border_radius=12
        )

        pygame.draw.rect(
            self.window,
            PINK,
            self.rect,
            width=2,
            border_radius=12
        )

        text_pos_x = self.rect.x + (self.rect.width - self.image.get_width()) // 2
        text_pos_y = self.rect.y + (self.rect.height - self.image.get_height()) // 2
        self.window.blit(self.image, (text_pos_x, text_pos_y))


class MultilineLabel(Label):
    def __init__(self, window, text, x, y, font_size, transparency=False, color=PINK):
        super().__init__(window, text, x, y, font_size, transparency, color)
        self.lines = text.split('\n')

        if len(self.lines) == 1:
            self.image = self.font.render(text, True, color)

        self.images = [self.font.render(line, True, color) for line in self.lines]
        self.max_width = max(image.get_width() for image in self.images)
        self.total_height = (
            sum(image.get_height() for image in self.images) +
            (len(self.lines) - 1) * font_size // 2
        )
        self.rect = pygame.Rect(x, y, self.max_width + 10, self.total_height + 10)
        self.max_lines = len(self.lines)

    def reset(self, text=''):
        self.max_width = self.total_height = 1
        self.transparency = False
        self.solved = False
        self.max_lines = 2
        self.set_text(f'{text}\n', 20)
        pygame.display.update()

    def set_text(self, new_text, font_size, color=PINK):
        self.font = pygame.font.SysFont('Verdana', font_size, bold=True)
        self.new_lines = new_text.split('\n')

        path_split = []

        if len(self.new_lines) > 1:
            for i in range(0, len(self.new_lines[1]), 60):
                path_split.append(self.new_lines[1][i:i + 60])

        self.lines = [self.new_lines[0]] + path_split
        self.max_lines = max(self.max_lines, len(self.lines))

        while len(self.lines) < self.max_lines:
            self.lines.append('')

        self.images = [self.font.render(line, True, color) for line in self.lines]
        self.max_width = max(self.max_width, max(image.get_width() for image in self.images))
        self.total_height = (
            sum(image.get_height() for image in self.images) +
            (len(self.lines) - 1) * font_size // 2
        )
        self.rect = pygame.Rect(self.x, self.y, self.max_width + 10, self.total_height + 10)
        self.draw()

    def draw(self):
        pygame.draw.rect(
            self.window,
            LIGHT_PINK if not self.solved else (220, 255, 220),
            self.rect,
            border_radius=8
        )

        pygame.draw.rect(
            self.window,
            PINK,
            self.rect,
            width=2,
            border_radius=8
        )

        offset = (
            (
                self.rect.height -
                sum(image.get_height() for image in self.images) -
                (len(self.images) - 1)
            ) // 2 + self.rect.y
        )

        for image in self.images:
            text_pos_x = self.rect.x + (self.rect.width - image.get_width()) // 2
            self.window.blit(image, (text_pos_x, offset))
            offset += image.get_height()


class LevelClear(Label):
    def __init__(self, window, text, x=256, y=192, font_size=60, color=PINK):
        super().__init__(window, text, x, y, font_size, color=color, width=512, height=256)

    def draw(self):
        transparent_surface = pygame.Surface(
            (self.rect.width, self.rect.height),
            pygame.SRCALPHA
        )
        transparent_surface.set_alpha(100)
        transparent_surface.fill((255, 235, 245))

        pygame.draw.rect(
            self.window,
            WHITE,
            self.rect,
            border_radius=15
        )

        pygame.draw.rect(
            self.window,
            PINK,
            self.rect,
            width=4,
            border_radius=15
        )

        text_pos_x = self.rect.x + (self.rect.width - self.image.get_width()) // 2
        text_pos_y = self.rect.y + (self.rect.height - self.image.get_height()) // 2

        self.window.blit(transparent_surface, (self.rect.x, self.rect.y))
        self.window.blit(self.image, (text_pos_x, text_pos_y))