import pygame, math
import inputs
from Globals import *

class Player:
    def __init__(self, x, y):
        self.width = 75
        self.height = 100
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.startPosition = (x, y) # to be able to reset the player's position on death
        # the feet are to determine if the player is on the ground by checking collision with the feet
        self.feetHeight = 5
        self.feetBufferX = 4 # so you can't walljump, otherwise the feet hitbox extends too far
        self.feet = pygame.Rect(x + self.feetBufferX, y - self.height - self.feetHeight, self.width - self.feetBufferX * 2, self.feetHeight)

        self.velocity = pygame.math.Vector2(0, 0)
        self.maxSpeed = pygame.math.Vector2(300, 600)
        self.acceleration = pygame.math.Vector2(1000, 900)
        self.friction = 2000
        self.direction = pygame.math.Vector2()
        self.jumpStr = -500 # jumpSTr is negative because the y axis goes down

        # max is the number of frames - 1, speed is the number of frames per second
        self.animations = {
            "walk": {"frames": [pygame.transform.scale(pygame.image.load("images/png/character/walk/walk" + str(i) + ".png").convert_alpha(), (self.width, self.height)) for i in range(1, 12)], "max": 11, "speed": 25},
            "idle": {"frames": [pygame.transform.scale(pygame.image.load("images/png/character/side.png").convert_alpha(), (self.width, self.height))], "max": 1, "speed": 0},
            "jump": {"frames": [pygame.transform.scale(pygame.image.load("images/png/character/jump.png").convert_alpha(), (self.width, self.height))], "max": 1, "speed": 0}
        }
        self.currentAnimation = "walk"
        self.currentFrame = 0.0

        self.moving = False
        self.grounded = False

        self.lookingRight = True # to know in wich direction the player is facing

        self.timers = {
            "coyoteJump": {"time": 0, "max": 0.2, "running": False, "looping": False}, # so the player can jump 0.2s after falling off a ledge
            "jumpBuffer": {"time": 0, "max": 0.2, "running": False, "looping": False} # so the player can jump even if they pressed the button 0.2s brfore landing on the ground
        }
    
        self.jumpSound = pygame.mixer.Sound("sfx/jump.wav")
        self.killSound = pygame.mixer.Sound("sfx/enemy.mp3")
        self.coinSound = pygame.mixer.Sound("sfx/coin1.wav")

        self.font = pygame.font.Font("images/game_over.ttf", 128)

        self.numCoins = 0
        self.giveCoins(0)
        self.coinImage = pygame.transform.scale(pygame.image.load("images/png/coin_silver.png"), (50, 50))

        self.dead = False
        # the rotation is for the death and next level animations
        self.rotation = 0
        self.rotationSpeed = 1040.0
        self.rotationMax = 360

        self.level = 1
        self.nextLevelSfx = pygame.mixer.Sound("sfx/chipquest.wav")

        self.keySfx = pygame.mixer.Sound("sfx/coin4.wav")
    
    def update(self, dt, blocks, enemies, coins, spikes, endAreas, keys, unlocked):
        keysPressed = pygame.key.get_pressed()
        self.handleAcceleration(dt, keysPressed)
        self.applyGravity(dt)
        self.applyFriction(dt)
        self.handleJump(keysPressed)
        was_grounded = self.grounded
        if not self.dead:
            unlocked = self.move(dt, blocks, enemies, coins, spikes, endAreas, keys, unlocked)
            if was_grounded and not self.grounded:
                self.timers["coyoteJump"]["running"] = True
            self.updateAnimations(dt)
            self.updateTimers(dt)
        else:
            # do a death dance :(
            self.rotation += self.rotationSpeed * dt
            if self.rotation > self.rotationMax:
                self.resetGame(enemies)
                unlocked = False
        
        return unlocked

    def draw(self):
        WINDOW.blit(self.coinImage, (10, 20))
        WINDOW.blit(self.coinText, (60, 0))
        if not self.dead:
            if self.lookingRight:
                WINDOW.blit(self.animations[self.currentAnimation]["frames"][math.floor(self.currentFrame)], (WINDOW_WIDTH / 2 - self.width / 2, WINDOW_HEIGHT / 2 - self.height / 2))
            else:
                WINDOW.blit(pygame.transform.flip(self.animations[self.currentAnimation]["frames"][math.floor(self.currentFrame)], True, False), (WINDOW_WIDTH / 2 - self.width / 2, WINDOW_HEIGHT / 2 - self.height / 2))
        else:
            if self.lookingRight:
                WINDOW.blit(pygame.transform.rotate(self.animations[self.currentAnimation]["frames"][math.floor(self.currentFrame)], self.rotation), (WINDOW_WIDTH / 2 - self.width / 2, WINDOW_HEIGHT / 2 - self.height / 2))
            else:
                WINDOW.blit(pygame.transform.rotate(pygame.transform.flip(self.animations[self.currentAnimation]["frames"][math.floor(self.currentFrame)], True, False), self.rotation), (WINDOW_WIDTH / 2 - self.width / 2, WINDOW_HEIGHT / 2 - self.height / 2))
    def updateAnimations(self, dt):
        if not self.grounded:
            self.currentAnimation = "jump"
        else:
            if self.moving:
                self.currentAnimation = "walk"
            else:
                self.currentAnimation = "idle"
        self.currentFrame += dt * self.animations[self.currentAnimation]["speed"]
        if self.currentFrame >= self.animations[self.currentAnimation]["max"]:
            self.currentFrame = 0.0
    
    def applyGravity(self, dt):
        self.velocity.y = min(self.velocity.y + self.acceleration.y * dt, self.maxSpeed.y) # so the player cannot fall faster than a certain speed
    
    def handleAcceleration(self, dt, keysPressed):
        self.moving = False
        # here I iterate over the inputs.left (list) and check to see if it is pressed so I can easily add more bindings
        for key in inputs.left:
            if keysPressed[key]:
                self.velocity.x = max(self.velocity.x - self.acceleration.x * dt, -self.maxSpeed.x)
                self.moving = True
                self.lookingRight = False
                break
        for key in inputs.right:
            if keysPressed[key]:
                self.velocity.x = min(self.velocity.x + self.acceleration.x * dt, self.maxSpeed.x)
                self.moving = True
                self.lookingRight = True
                break
    
    def applyFriction(self, dt):
        # if the player is not moving or he is moving in the opposite direction of where he is facing
        if not self.moving or self.lookingRight != (self.velocity.x > 0):
            self.velocity = self.velocity.move_towards(pygame.math.Vector2(0, self.velocity.y), self.friction * dt)
    
    def handleJump(self, keysPressed):
        pressed = False
        for key in inputs.jump:
            if keysPressed[key]:
                pressed = True
                break
        if pressed or self.timers["jumpBuffer"]["running"]:
            if self.grounded or self.timers["coyoteJump"]["running"]:
                self.timers["jumpBuffer"]["running"] = False
                self.timers["jumpBuffer"]["time"] = 0.0
                self.timers["coyoteJump"]["running"] = False
                self.timers["coyoteJump"]["time"] = 0.0
                self.velocity.y = self.jumpStr
                self.jumpSound.play()
                self.grounded = False
            else:
                self.timers["jumpBuffer"]["running"] = True
        else:
            if not self.grounded and self.velocity.y < self.jumpStr / 4:
                self.velocity.y = self.jumpStr / 4
    
    def move(self, dt, blocks, enemies, coins, spikes, endAreas, keys, unlocked):
        self.moveSingleAxis(dt, blocks, "x", unlocked) # I move the player one axis at a time to avoid bugs
        self.moveSingleAxis(dt, blocks, "y", unlocked)
        self.feet.topleft = self.rect.bottomleft
        self.feet.left += self.feetBufferX
        

        # check if the player is grounded by checking collision with the feet
        collideIndex = -1
        for i, block in enumerate(blocks):
            if type(block["rect"]) is pygame.rect.Rect and not (block["disappearing"] and unlocked):
                if self.feet.colliderect(block["rect"]):
                    collideIndex = i
                    break
        if collideIndex != -1:
            self.grounded = True
            self.velocity.y = min(0, self.velocity.y)
        else:
            self.grounded = False
        
        # allow the player to kill enemies by jumping on them
        collideIndex = self.feet.collidelist(enemies)
        if collideIndex != -1:
            if enemies[collideIndex].alive:
                enemies[collideIndex].alive = False
                self.killSound.play()
                self.velocity.y = self.jumpStr
        
        # check if the player collided with an enemy (death)
        collideIndex = -1
        for i, enemy in enumerate(enemies):
            if enemy.alive and self.rect.colliderect(enemy.rect):
                collideIndex = i
                break
        if collideIndex != -1:
            self.dead = True
        
        collideIndex = -1
        for i, coin in enumerate(coins):
            if self.rect.colliderect(coin["rect"]):
                collideIndex = i
                break
        if collideIndex != -1:
            self.giveCoins(1)
            coins.pop(collideIndex)
        
        for spike in spikes:
            if self.rect.colliderect(spike.rect):
                self.dead = True
                break
        
        for endArea in endAreas:
            if self.rect.colliderect(endArea["rect"]):
                self.nextLevel()
        
        if (not unlocked) and self.rect.collidelist(keys) != -1:
            unlocked = True
            self.keySfx.play()
        
        return unlocked

    def moveSingleAxis(self, dt, blocks, axis, unlocked):
        if axis == "x":
            movedRect = self.rect.move(self.velocity.x * dt, 0)
        else:
            movedRect = self.rect.move(0, self.velocity.y * dt)
        self.feet.topleft = movedRect.bottomleft
        self.feet.left += self.feetBufferX
        # check for collision before moving the player 
        colliding = False
        collideIndex = -1
        for i, block in enumerate(blocks):
            if type(block["rect"]) is pygame.rect.Rect:
                if movedRect.colliderect(block["rect"]):
                    if not (block["disappearing"] and unlocked): # check if the block has disapeared
                        collideIndex = i
                        break
        if collideIndex != -1:
            if not (blocks[collideIndex]["disappearing"] and unlocked):
                colliding = True
                if type(blocks[collideIndex]["rect"]) is pygame.rect.Rect:
                    if axis == "y":
                        if self.feet.colliderect(blocks[collideIndex]["rect"]):
                            self.rect.bottom = blocks[collideIndex]["rect"].top
                        self.velocity.y = 0

        if not colliding:
            self.rect = movedRect
    
    def updateTimers(self, dt):
        for k_timer in self.timers: # k_timer stands for key_timer (the timers key in the dict)
            timer = self.timers[k_timer]
            if timer["running"]:
                timer["time"] += dt
                if timer["time"] > timer["max"]:
                    if timer["looping"]:
                        timer["time"] = 0.0
                    else:
                        timer["running"] = False
                        timer["time"] = 0.0
            else:
                timer["time"] = 0.0
    
    def resetGame(self, enemies):
        for enemy in enemies:
            enemy.alive = True
            enemy.rect.topleft = enemy.startPosition
            enemy.lookingRight = False
        self.rect.topleft = self.startPosition
        self.velocity.xy = (0, 0)
        self.dead = False
        self.rotation = 0.0
        self.lookingRight = True
        self.timers["jumpBuffer"]["time"] = 0.0
        self.timers["jumpBuffer"]["running"] = False
    
    def giveCoins(self, amount):
        self.numCoins += amount
        self.coinSound.play()
        self.coinText = self.font.render("x" + str(self.numCoins), False, (255, 255, 255))
    
    def nextLevel(self):
        self.level += 1
        self.nextLevelSfx.play()
        # do a cool little victory dance!
        while self.rotation < self.rotationMax:
            self.rotation += self.rotationSpeed * 1/30
            rotatedImage = pygame.transform.rotate(self.animations["jump"]["frames"][0], self.rotation)
            self.rectImage = rotatedImage.get_rect(center=self.rect.center)
            WINDOW.blit(rotatedImage, (WINDOW_WIDTH / 2 - self.width / 2, WINDOW_HEIGHT / 2 - self.height / 2))
            pygame.display.update()
            fpsClock.tick(30)
        