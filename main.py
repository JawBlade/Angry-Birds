import pygame
import pymunk
import pymunk.pygame_util
import os
from helpers import image
from objects import Box
from birds import bird
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
box_1_body = Box((40, 100), (1125, 517), image_path="images/box.jpeg")
box_1 = box_1_body.create(space)

# create box with its image owned by the Box instance
box_2_body = Box((40, 100), (1000, 517), image_path="images/box.jpeg")
box_2 = box_2_body.create(space)

# Adds Floor
floor_body = space.static_body
floor_body.position = (0, 567)
floor = pymunk.Segment(floor_body, (0, 0), (1280, 0), 1)
floor.color = (103, 177, 20, 0)
space.add(floor)

red_body = bird(0.6, 27, (70,501), image_path="images/red_bird.webp")
red = red_body.create(space)


# Adds Images
background_image = image('images/back.jpg', (width, height))
sling_shot = image('images/sling_stick.png', (300,300))
sling_shot2 = image('images/sling_stick2.png', (300,300))
pig = image("images/pig.webp", (64, 64))


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if background_image:
        screen.blit(background_image, (0,0))
        screen.blit(sling_shot, (75,320))
        screen.blit(sling_shot2, (75,320))
        screen.blit(pig, (1025,505))
    else:
        screen.fill("black")

    space.debug_draw(draw_options)
    
    box_1_body.mask(screen, box_1)
    box_2_body.mask(screen, box_2)
    red_body.mask(screen, red)

    pygame.display.flip()

    clock.tick(60)
    space.step(1.0 / 60.0)

pygame.quit()

# where I got the Bird images
# https://angrybirdsfanon.fandom.com/wiki/Angry_Birds_Chrome/Classic_artwork/sprites_Collection#Purple_Bird