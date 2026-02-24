import pygame
import pymunk
import pymunk.pygame_util
import os
from helpers import image
from objects import Box
import math


width, height = (1280, 720)
pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True

# Setup Space
space = pymunk.Space()
space.gravity = (0,900)
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Adds the boxes
square = Box((100, 100), (1280 // 2, 720 // 2), "brown")
body, box = square.create()
space.add(body, box)

bbox = Box((50, 100), (900, 720 // 2), "brown")
body, box = bbox.create()
space.add(body, box)

# Adds Floor
floor_body = space.static_body
floor_body.position = (0, 567)
floor = pymunk.Segment(floor_body, (0, 0), (1280, 0), 1)
floor.color = (103, 177, 20, 0)
space.add(floor)

# Adds Images
background_image = image('images/back.jpg', (width, height))
sling_shot = image('images\slingshot.png', (200,300))
red = image("images/red_bird.webp", (64, 64))

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if background_image:
        screen.blit(background_image, (0,0))
        screen.blit(sling_shot, (100,320))
        screen.blit(red, (70,505))
    else:
        screen.fill("black")
    
    space.debug_draw(draw_options) # Draws Box on every frame

    pygame.display.flip()

    clock.tick(60)
    space.step(1.0 / 60.0)

pygame.quit()

# where I got the Bird images
# https://angrybirdsfanon.fandom.com/wiki/Angry_Birds_Chrome/Classic_artwork/sprites_Collection#Purple_Bird