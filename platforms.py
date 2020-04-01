import pygame as pygame
from settings import *

# lightweight class, only purpose is to represent the games Platforms
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        self.image = pygame.Surface((width, height))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
    def update(self):
        pygame.sprite.Sprite.update(self)
    
    def draw(self, surface):
        surface.blit(self.image,self.rect)