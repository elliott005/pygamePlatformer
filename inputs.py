import pygame
from pygame.locals import K_RIGHT, K_LEFT, K_SPACE, K_UP, K_ESCAPE, K_q, K_d, K_z, K_r

# This file is for configuring the input system. to add a binding, simply import the key from pygame.locals(above)
# and and add it to one of the lists below, depending on what you want to bind it to.
# In the code, we will iterate over each of these lists and check if one of the keys is pressed.

left = [K_LEFT, K_q]
right = [K_RIGHT, K_d]
jump = [K_SPACE, K_UP, K_z]
reset = [K_r]
quit = [K_ESCAPE]
