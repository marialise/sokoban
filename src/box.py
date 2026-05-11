import pygame
from pygame.sprite import Sprite


# ============================================
# BOX / GIFT
# ============================================
class Box(Sprite):

    def __init__(self, *groups, x, y, game=None):

        super().__init__(*groups)

        self.game = game

        # ====================================
        # GIFT NORMAL
        # ====================================
        self.sprite = pygame.image.load(
            'img/gift.png'
        ).convert_alpha()

        self.sprite = pygame.transform.scale(
            self.sprite,
            (90, 90)
        )

        # ====================================
        # GIFT DI TARGET
        # ====================================
        self.spriteg = pygame.image.load(
            'img/giftT.png'
        ).convert_alpha()

        self.spriteg = pygame.transform.scale(
            self.spriteg,
            (90, 90)
        )

        # ====================================
        # IMAGE AWAL
        # ====================================
        if game and game.puzzle[y, x].ground:
            self.image = self.spriteg
        else:
            self.image = self.sprite

        # ====================================
        # RECT
        # ====================================
        self.rect = self.image.get_rect()

        # CENTER KE TILE
        self.rect.topleft = (
            x * 64 - 13,
            y * 64 - 13
        )

        self.x = x
        self.y = y

    # ========================================
    # MOVE
    # ========================================
    def can_move(self, move):

        target_x = self.x + move[0] // 64
        target_y = self.y + move[1] // 64

        target = (target_y, target_x)
        curr = (self.y, self.x)

        target_elem = self.game.puzzle[target]

        if not isinstance(target_elem.obj, Box):

            curr_elem = self.game.puzzle[curr]

            # UPDATE DATA
            self.x = target_x
            self.y = target_y

            # UPDATE VISUAL
            self.rect.topleft = (
                target_x * 64 - 13,
                target_y * 64 - 13
            )

            # UPDATE TILE LAMA
            curr_elem.char = (
                '-' if not curr_elem.ground else 'X'
            )

            curr_elem.obj = None

            # UPDATE TILE BARU
            target_elem.char = (
                '@' if not target_elem.ground else '$'
            )

            target_elem.obj = self

            # UPDATE SPRITE
            self.update_sprite()

            return True

        return False

    # ========================================
    # REVERSE MOVE
    # ========================================
    def reverse_move(self, move):

        target = (
            self.y + move[0] // 64,
            self.x + move[1] // 64
        )

        curr_pos = (self.y, self.x)

        self.game.puzzle[curr_pos].obj = None
        self.game.puzzle[target].obj = self

        self.y, self.x = target

        self.rect.topleft = (
            target[1] * 64 - 13,
            target[0] * 64 - 13
        )

        self.game.puzzle[curr_pos].char = (
            'X'
            if self.game.puzzle[curr_pos].ground
            else '-'
        )

        self.game.puzzle[target].char = (
            '$'
            if self.game.puzzle[target].ground
            else '@'
        )

        self.update_sprite()

    # ========================================
    # UPDATE SPRITE
    # ========================================
    def update_sprite(self):

        curr_obj = self.game.puzzle[self.y, self.x]

        if curr_obj and curr_obj.ground:
            self.image = self.spriteg
        else:
            self.image = self.sprite

        old_x = self.rect.x
        old_y = self.rect.y

        self.rect = self.image.get_rect()

        self.rect.topleft = (
            old_x,
            old_y
        )

    # ========================================
    # DELETE
    # ========================================
    def __del__(self):

        self.kill()


class Obstacle(Box):

    def __init__(self, *groups, x, y):

        super().__init__(*groups, x=x, y=y)

        raw_image = pygame.image.load(
            'img/boxCute.png'
        ).convert_alpha()

        # AUTO CROP TRANSPARAN
        crop_rect = raw_image.get_bounding_rect()
        cropped_image = raw_image.subsurface(crop_rect)

        # SIZE
        self.image = pygame.transform.scale(
            cropped_image,
            (68, 68)
        )

        self.rect = self.image.get_rect()

        # CENTER
        self.rect.topleft = (
            x * 64 - 2,
            y * 64 - 2
        )