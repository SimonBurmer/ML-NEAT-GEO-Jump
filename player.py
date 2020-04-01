import pygame as pg
from settings import *
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, game):
        self.game = game
        self.image = pg.Surface((30, 40))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vellocity = vec(0, 0) #player speed 
        self.acceleration = vec(0, 0) #player accelertion
        self.left = False
        self.right = False

    def jump(self):
        #jump only if standing on a platform
        hits = pg.sprite.spritecollide(self, self.game.platforms, False)

        if hits:
            self.vellocity.y = -PLAYER_JUMP
            
    def update(self):
        self.acceleration = vec(0, PLAYER_GRAV)
        #movent
        keys = pg.key.get_pressed()
        if self.left:
            self.acceleration.x = -PLAYER_ACC #acceleration left
            self.left = False
        if self.right:
            self.acceleration.x = PLAYER_ACC #accelertion right
            self.right = False

        #apply friction
        self.acceleration.x += self.vellocity.x * PLAYER_FRICTION
        #equations of motion
        self.vellocity += self.acceleration
        self.pos += self.vellocity + 0.5 * self.acceleration

        #infinity screen
        if self.pos.x > WIDTH:
            self.pos.x = 0
        if self.pos.x < 0:
            self.pos.x = WIDTH

        self.rect.midbottom = self.pos
    
    def draw(self, surface):
        surface.blit(self.image,self.rect)