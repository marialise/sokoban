# src/assets.py
import pygame

_cache = {}

def load(path, size=None):
    key = (path, size)
    if key not in _cache:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        _cache[key] = img
    return _cache[key]  # semua sprite pakai surface yang sama

def preload_all():
    """Panggil sekali saat startup."""
    load('img/ubin.png', (64, 64))
    load('img/sidefloor.png', (64, 64))
    load('img/paw.png', (76, 76))
    load('img/gift.png', (90, 90))
    load('img/giftT.png', (90, 90))
    load('img/boxCute.png', (68, 68))
    load('img/playerU.png', (64, 64))
    load('img/playerD.png', (64, 64))
    load('img/playerL.png', (64, 64))
    load('img/playerR.png', (64, 64))
    load('img/logo.png', (300, 300))