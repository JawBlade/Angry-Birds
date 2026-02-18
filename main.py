import pygame
import pymunk
import pymunk.pygame_util
import os
from objects import Box
import math


height, width = (1280, 720)
pygame.init()
screen = pygame.display.set_mode((height, width))
clock = pygame.time.Clock()
running = True

# Setup Space
space = pymunk.Space()
space.gravity = (0,900)
draw_options = pymunk.pygame_util.DrawOptions(screen)

box_1 = Box(100,100)

body, box = box_1

space.add(body, box)

background_image = pygame.image.load(os.path.join('images/back.jpg')).convert()
background_image = pygame.transform.scale(background_image, (height, width))

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if background_image:
        screen.blit(background_image, (0,0))
    else:
        screen.fill("black")

    space.debug_draw(draw_options) # Draws Box on every frame

    pygame.display.flip()

    clock.tick(60)

pygame.quit()