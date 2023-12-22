import pygame, math
from Globals import *

class Enemy:
    animations = {
            "walk": {"frames": [pygame.transform.scale(pygame.image.load("images/png/enemies/slime_walk.png").convert_alpha(), (50, 50))], "max": 1, "speed": 0},
            "idle": {"frames": [pygame.transform.scale(pygame.image.load("images/png/enemies/slime_normal.png").convert_alpha(), (50, 50))], "max": 1, "speed": 0},
            "dead": {"frames": [pygame.transform.scale(pygame.image.load("images/png/enemies/slime_dead.png").convert_alpha(), (50, 15))], "max": 1, "speed": 0}
        }
    deathSound = pygame.mixer.Sound("sfx/enemy.mp3")
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 50, 50)
        self.startPosition = (x, y)
        self.speed = pygame.math.Vector2(100, 0)
        self.gravity = 900
        self.gravityMax = 600
        self.currentAnimation = "idle"
        self.currentFrame = 0.0

        self.moving = False
        self.lookingRight = False

        self.moveDistance = 300

        self.alive = True
    
    def update(self, dt, blocks, enemies, spikes, PlayerX, unlocked):
        if self.alive:
            self.move(dt, blocks, spikes, enemies, unlocked)
            self.updateMovement(PlayerX)
        self.updateAnimations(dt)

    def draw(self, playerPos):
        x, y = playerPos
        if self.currentAnimation != "dead":
            if not self.lookingRight:
                WINDOW.blit(self.animations[self.currentAnimation]["frames"][math.floor(self.currentFrame)], (self.rect.left - x + WINDOW_WIDTH / 2, self.rect.top - y + WINDOW_HEIGHT / 2))
            else:
                WINDOW.blit(pygame.transform.flip(self.animations[self.currentAnimation]["frames"][math.floor(self.currentFrame)], True, False), (self.rect.left - x + WINDOW_WIDTH / 2, self.rect.top - y + WINDOW_HEIGHT / 2))
        else:
            if not self.lookingRight:
                WINDOW.blit(self.animations[self.currentAnimation]["frames"][math.floor(self.currentFrame)], (self.rect.left - x + WINDOW_WIDTH / 2, self.rect.top - y + WINDOW_HEIGHT / 2 + self.rect.height - 15))
            else:
                WINDOW.blit(pygame.transform.flip(self.animations[self.currentAnimation]["frames"][math.floor(self.currentFrame)], True, False), (self.rect.left - x + WINDOW_WIDTH / 2, self.rect.top - y + WINDOW_HEIGHT / 2 + self.rect.height - 15))

    def move(self, dt, blocks, spikes, enemies, unlocked):
        if self.moving:
            self.speed.y = max(self.speed.y + self.gravity * dt, self.gravityMax)
            if self.lookingRight:
                self.speed.x = 200
            else:
                self.speed.x = -200
            self.moveSingleAxis(dt, blocks, enemies, "x", unlocked)
            self.moveSingleAxis(dt, blocks, enemies, "y", unlocked)
        for spike in spikes:
            if self.rect.colliderect(spike.rect):
                self.alive = False
                self.deathSound.play()
    
    def moveSingleAxis(self, dt, blocks, enemies, axis, unlocked):
        if axis == "x":
            movedRect = self.rect.move(self.speed.x * dt, 0)
        else:
            movedRect = self.rect.move(0, self.speed.y * dt)
        colliding = False
        collideIndex = -1
        for i, block in enumerate(blocks):
            if type(block["rect"]) is pygame.rect.Rect:
                if not (block["disappearing"] and unlocked):
                    if movedRect.colliderect(block["rect"]):
                        collideIndex = i
                        break
        collideIndexEnemies = -1
        for i, enemy in enumerate(enemies):
            if enemy.rect == self.rect: continue
            if movedRect.colliderect(enemy.rect):
                collideIndexEnemies = i
                break
        if collideIndex != -1 or collideIndexEnemies != -1:
            colliding = True
            if axis == "y":
                self.speed.y = 0
                self.speed.y = 0
            else:
                self.lookingRight = not self.lookingRight

        if not colliding:
            self.rect = movedRect

    def updateMovement(self, playerX):
        self.moving = abs(playerX - self.rect.centerx) < self.moveDistance

    def updateAnimations(self, dt):
        if not self.alive:
            self.currentAnimation = "dead"
        else:
            if self.moving:
                self.currentAnimation = "walk"
            else:
                self.currentAnimation = "idle"
        self.currentFrame += dt * self.animations[self.currentAnimation]["speed"]
        if self.currentFrame >= self.animations[self.currentAnimation]["max"]:
            self.currentFrame = 0.0