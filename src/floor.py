import pygame
from .assets import load


class Floor(pygame.sprite.Sprite):

    def __init__(self, *groups, x, y):

        super().__init__(*groups)

        if x <= 15:
            self.image = load('img/ubin.png', (64, 64))
        else:
            self.image = load('img/sidefloor.png', (64, 64))

        self.rect = pygame.Rect(
            x * 64,
            y * 64,
            64,
            64
        )

        self.x = x
        self.y = y

    def draw(self, surface):

        surface.blit(
            self.image,
            self.rect
        )

    def __del__(self):

        self.kill()


# ============================================
# GOAL / PAW
# ============================================
class Goal(Floor):

    def __init__(self, *groups, x, y):

        super().__init__(*groups, x=x, y=y)

        self.image = load('img/paw.png', (76, 76))

        # RECT IKUT IMAGE
        self.rect = self.image.get_rect()

        # CENTER KE TILE
        self.rect.topleft = (
            x * 64 - 6,
            y * 64 - 6
        )