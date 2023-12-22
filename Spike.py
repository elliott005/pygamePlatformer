import pygame
from levels.level1 import tileSize
from random import randint
from Globals import *

class Spike:
    image = pygame.transform.scale(pygame.image.load("images/SawSmall.png").convert_alpha(), (tileSize, tileSize))
    def __init__(self, x, y):
        self.buffer = 20
        self.rect = pygame.Rect(x + self.buffer, y + self.buffer, tileSize - self.buffer * 2, tileSize - self.buffer * 2)
        self.rotation = randint(0, 360)
        self.rotationSpeed = 360.0
    
    def update(self, dt):
        self.rotation += self.rotationSpeed * dt
        if self.rotation >= 720:
            self.rotation = 0.0
    
    def draw(self, playerPos):
        x, y = playerPos
        rotatedImage = pygame.transform.rotate(self.image, self.rotation)
        self.rectImage = rotatedImage.get_rect(center=self.rect.center)
        WINDOW.blit(rotatedImage, (self.rectImage.left - x + WINDOW_WIDTH / 2, self.rectImage.top - y + WINDOW_HEIGHT / 2))