import pygame, sys, random, csv
import os.path
from pygame.locals import *
pygame.init()
 
BACKGROUND = (120, 100, 255)
RED = (255, 30, 70)
BLUE = (10, 20, 200)
GREEN = (50, 230, 40)

from Globals import *

import inputs
from Player import Player
import levels.level1 as level1
import levels.level2 as level2
import levels.level3 as level3
import levels.level4 as level4
import levels.level5 as level5
import levels.level6 as level6
import levels.level7 as level7
import levels.level8 as level8
from Enemy import Enemy
from Spike import Spike

mainTheme = pygame.mixer.Sound("sfx/Stage1.wav")

def main():
    levels = {"1": level1, "2": level2, "3": level3, "4": level4, "5": level5, "6": level6, "7": level7, "8": level8}
    level = "1"
    numCoins = 0
    unlocked = False
    if os.path.isfile("./save.csv"):
        with open("save.csv", "r") as save:
            csvReader = csv.reader(save)
            for i, row in enumerate(csvReader):
                if i == 0:
                    level = row[0]
                    numCoins = int(row[1])

    blocks, enemies, player, coins, spikes, endAreas, keys = createWorld(levels[level])
    keyImage = pygame.transform.scale(pygame.image.load("images/png/key_red.png").convert_alpha(), (levels[level].tileSize, levels[level].tileSize))
    player.giveCoins(numCoins)
    player.level = int(level)
    if mainTheme.get_num_channels() == 0:
        mainTheme.play(loops=-1)
    while 1:
        for event in pygame.event.get() :
            if event.type == QUIT:
                print(fpsClock.get_fps())
                with open("save.csv", "w") as save:
                    save.write(level + "," + str(player.numCoins))
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                for key in inputs.quit:
                    if event.key == key:
                        print(fpsClock.get_fps())
                        with open("save.csv", "w") as save:
                            save.write(level + "," + str(player.numCoins))
                        pygame.quit()
                        sys.exit()
                        break
                for key in inputs.reset:
                    if event.key == key:
                        main()
                        break
        
        dt = fpsClock.get_time() / 1000
        
        levelStart = player.level
        unlocked = player.update(dt, blocks, enemies, coins, spikes, endAreas, keys, unlocked)
        if levelStart != player.level:
            level = str(player.level)
            if int(level) >= len(levels):
                level = str(len(levels))
            numCoins = player.numCoins
            blocks, enemies, player, coins, spikes, endAreas, keys = createWorld(levels[level])
            unlocked = False
            player.giveCoins(numCoins)
            player.level = int(level)
        
        WINDOW.fill(BACKGROUND)

        drawWorld(blocks, player.rect.center, unlocked)

        for enemy in enemies:
            if abs(enemy.rect.top - player.rect.top) < WINDOW_HEIGHT and abs(enemy.rect.left - player.rect.left) < WINDOW_WIDTH:
                enemy.update(dt, blocks, enemies, spikes, player.rect.centerx, unlocked)
                enemy.draw(player.rect.center)
        
        for coin in coins:
            WINDOW.blit(coin["image"], (coin["rect"].left - player.rect.centerx + WINDOW_WIDTH / 2, coin["rect"].top - player.rect.centery + WINDOW_HEIGHT / 2))
        
        for endArea in endAreas:
            WINDOW.blit(endArea["image"], (endArea["rect"].left - player.rect.centerx + WINDOW_WIDTH / 2, endArea["rect"].top - player.rect.centery + WINDOW_HEIGHT / 2))
        
        for spike in spikes:
            spike.update(dt)
            spike.draw(player.rect.center)

        if not unlocked:
            for key in keys:
                WINDOW.blit(keyImage, (key.left - player.rect.centerx + WINDOW_WIDTH / 2, key.top - player.rect.centery + WINDOW_HEIGHT / 2))

        player.draw()

        # print(fpsClock.get_fps())

        pygame.display.update()
        fpsClock.tick(FPS)

def drawWorld(blocks, playerpos, unlocked):
    playerX, playerY = playerpos
    for block in blocks:
        if type(block["rect"]) is pygame.rect.Rect:
            if not (block["disappearing"] and unlocked):
                if abs(block["rect"].top - playerY) < WINDOW_HEIGHT and abs(block["rect"].left - playerX) < WINDOW_WIDTH:
                    WINDOW.blit(block["image"], (block["rect"].left - playerX + WINDOW_WIDTH / 2, block["rect"].top - playerY + WINDOW_HEIGHT / 2))
        elif abs(block["rect"][1] - playerY) < WINDOW_HEIGHT and abs(block["rect"][0] - playerX) < WINDOW_WIDTH:
            WINDOW.blit(block["image"], (block["rect"][0] - playerX + WINDOW_WIDTH / 2, block["rect"][1] - playerY + WINDOW_HEIGHT / 2))

def createWorld(tilemap):
    blocks = []
    enemies = []
    coins = []
    spikes = []
    endAreas = []
    keys = []
    player = Player(0, 0)
    grass = pygame.transform.scale(pygame.image.load("images/png/ground.png").convert_alpha(), (tilemap.tileSize, tilemap.tileSize))
    dirt = pygame.transform.scale(pygame.image.load("images/png/ground_dirt.png").convert_alpha(), (tilemap.tileSize, tilemap.tileSize))
    plant = pygame.transform.scale(pygame.image.load("images/png/alien_plant.png").convert_alpha(), (tilemap.tileSize, tilemap.tileSize / 2))
    block = pygame.transform.scale(pygame.image.load("images/png/block.png").convert_alpha(), (tilemap.tileSize, tilemap.tileSize))
    bush = pygame.transform.scale(pygame.image.load("images/png/bush.png").convert_alpha(), (tilemap.tileSize, tilemap.tileSize / 2))
    crate = pygame.transform.scale(pygame.image.load("images/png/crate.png").convert_alpha(), (tilemap.tileSize, tilemap.tileSize))
    shroom = pygame.transform.scale(pygame.image.load("images/png/shroom.png").convert_alpha(), (tilemap.tileSize, tilemap.tileSize / 2))
    coin = pygame.transform.scale(pygame.image.load("images/png/coin_silver.png").convert_alpha(), (tilemap.tileSize, tilemap.tileSize))
    coinGold = pygame.transform.scale(pygame.image.load("images/png/coin_gold.png").convert_alpha(), (tilemap.tileSize, tilemap.tileSize))
    lock = pygame.transform.scale(pygame.image.load("images/png/lock_red.png").convert_alpha(), (tilemap.tileSize, tilemap.tileSize))
    for y, row in enumerate(tilemap.map):
        for x, tile in enumerate(row):
            if tile == 1:
                rect = pygame.Rect(x * tilemap.tileSize, y * tilemap.tileSize, tilemap.tileSize, tilemap.tileSize)
                if random.randint(1, 7) == 1:
                    image = block
                else:
                    if tilemap.map[max(y - 1, 0)][min(x, len(tilemap.map[max(y - 1, 0)]) - 1)] == 1:
                        image = dirt
                    else:
                        if tilemap.map[y][max(x - 1, 0)] == 0 and tilemap.map[y][min(x + 1, len(tilemap.map[y]) - 1)] == 0:
                            image = crate
                        else:
                            image = grass
                            if random.randint(1, 4) == 1:
                                n = random.randint(1, 4)
                                if n == 1:
                                    blocks.append({"rect": (x * tilemap.tileSize, (y - 0.5) * tilemap.tileSize), "image": shroom})
                                elif n == 2:
                                    blocks.append({"rect": (x * tilemap.tileSize, (y - 0.5) * tilemap.tileSize), "image": bush})
                                else:
                                    blocks.append({"rect": (x * tilemap.tileSize, (y - 0.5) * tilemap.tileSize), "image": plant})
                blocks.append({"rect": rect, "image": image, "disappearing": False})
            elif tile == 2:
                enemies.append(Enemy(x * tilemap.tileSize, y * tilemap.tileSize))
            elif tile == "P":
                player = Player(x * tilemap.tileSize, (y - 0.5) * tilemap.tileSize)
            elif tile == 3:
                coins.append({"rect": pygame.Rect(x * tilemap.tileSize, y * tilemap.tileSize, tilemap.tileSize, tilemap.tileSize), "image": coin})
            elif tile == 4:
                spikes.append(Spike(x * tilemap.tileSize, y * tilemap.tileSize))
            elif tile == 5:
                endAreas.append({"rect": pygame.Rect(x * tilemap.tileSize, y * tilemap.tileSize, tilemap.tileSize, tilemap.tileSize), "image": coinGold})
            elif tile == 6:
                blocks.append({"rect": pygame.Rect(x * tilemap.tileSize, y * tilemap.tileSize, tilemap.tileSize, tilemap.tileSize), "image": lock, "disappearing": True})
            elif tile == 7:
                keys.append(pygame.Rect(x * tilemap.tileSize, y * tilemap.tileSize, tilemap.tileSize, tilemap.tileSize))
    return blocks, enemies, player, coins, spikes, endAreas, keys

if __name__ == "__main__":
    main()