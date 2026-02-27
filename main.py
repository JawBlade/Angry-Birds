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
square = Box((40, 100), (1125, 517), image_path="images/box.jpeg")
square_b, box = square.create(space)

# create box with its image owned by the Box instance
bbox = Box((40, 100), (1000, 517), image_path="images/box.jpeg")
bbox_b, box = bbox.create(space)

# Adds Floor
floor_body = space.static_body
floor_body.position = (0, 567)
floor = pymunk.Segment(floor_body, (0, 0), (1280, 0), 1)
floor.color = (103, 177, 20, 0)
space.add(floor)










mass = 10
radius = 25
# Calculate the moment of inertia (Pymunk can do this automatically for basic shapes)
moment = pymunk.moment_for_circle(mass, 0, radius)

# 3. Create a Body
# A dynamic body moves and responds to forces.
# Arguments are mass and moment of inertia.
body = pymunk.Body(mass, moment)
body.position = (300, 400) # Set the initial position (x, y)

# 4. Create a Circle shape and associate it with the body
# Arguments are the body, radius, and an optional offset from the body's center of gravity.
circle_shape = pymunk.Circle(body, radius)
circle_shape.friction = 0.5
circle_shape.elasticity = 0.8 # Bounciness

# 5. Add the body and shape to the space
space.add(body, circle_shape)













# Adds Images
background_image = image('images/back.jpg', (width, height))
sling_shot = image('images/slingshot.png', (300,300))
red = image("images/red_bird.webp", (64, 64))
pig = image("images/pig.webp", (64, 64))


while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if background_image:
        screen.blit(background_image, (0,0))
        screen.blit(sling_shot, (75,320))
        screen.blit(red, (70,501))
        screen.blit(pig, (1025,505))
    else:
        screen.fill("black")

    space.debug_draw(draw_options)
    
    bbox.mask(screen, square_b)
    square.mask(screen, bbox_b)

    pygame.display.flip()

    clock.tick(60)
    space.step(1.0 / 60.0)

pygame.quit()

# where I got the Bird images
# https://angrybirdsfanon.fandom.com/wiki/Angry_Birds_Chrome/Classic_artwork/sprites_Collection#Purple_Bird