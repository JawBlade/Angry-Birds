import pygame
import pymunk
import pymunk.pygame_util
import os
from helpers import image, create_band, snap_check, grab, make_box, respawn, clamp_vels
from characters import Pig, Bird
import math

# This is just Boiler Plate
pygame.display.set_caption('Knock-Off Angry Birds')

pygame.init()

WIDTH, HEIGHT = (1280, 720)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

space = pymunk.Space()
space.gravity = (0,900)
space.damping = 0.65
draw_options = pymunk.pygame_util.DrawOptions(screen)

# Make the different boxes for the level
boxes = [
    make_box((40, 100), (1125, 517), space),
    make_box((40, 100), (1000, 517), space),
]

# Adds Floor
floor_body = space.static_body
floor_body.position = (0, 567)
floor = pymunk.Segment(floor_body, (0, 0), (1280, 0), 1)
floor.friction = 1
floor.color = (103, 177, 20, 0)
space.add(floor)

# Adds the bird's body to our space
red_body = Bird(0.6, 27, (225,410), image_path="images/red2.webp")
red = red_body.create(space)

# Vars for loop
band = pygame.Surface((10, 20), pygame.SRCALPHA)
band.fill((159, 26, 13))

pig_b = Pig(1, 27, (1063,540), image_path="images/pig.webp")
pig = pig_b.create(space)

running   = True
released  = False
dragging  = False
idle      = True
launch    = False
SLING_POS = (225, 410)

while running:
    bird_x, bird_y = red.position
    mouse_pos = pygame.mouse.get_pos()

    # Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            bird_x, bird_y = red.position
            mouse_x, mouse_y = event.pos
            dist = math.hypot(bird_x - mouse_x, bird_y - mouse_y) 
            if dist < 40 and not launch:
                dragging = True
                released = False

            if grab(mouse_pos, red, released, launch):
                is_dragging = True

        if event.type == pygame.MOUSEBUTTONUP: 
            # Launching stuff
            if dragging and not launch:
                dragging = False
                released = True
                px, py = red.position
                offset_x = 225 - px
                offset_y = 410 - py
                POWER = 12
                red.body_type = pymunk.Body.DYNAMIC
                red.velocity = (offset_x * POWER, offset_y * POWER)

    button = pygame.mouse.get_pressed()

    # Logic for different states
    if dragging:
            idle = False
    elif idle == True:
            red.position = SLING_POS
            red.velocity = (0, 0)
    elif released == True:
        launch = True
    if launch and red.velocity.length <= 5:
        released, dragging, idle, launch = respawn(red)

    released = snap_check(red, released) 

    clamp_vels(space)
    space.step(1.0 / 60.0)
    
    dx, dy = bird_x - 225, bird_y - 410 
    angle_to_bird = math.atan2(dy, dx)
    attach_point = (bird_x + math.cos(angle_to_bird) * 36, bird_y + math.sin(angle_to_bird) * 36)
    
    # Drawing Logic like the visuals: Bakcgroud, bird, pig, Slingshot, and boxes
    screen.blit(image('images/back.jpg', (WIDTH, HEIGHT)), (0,0))
    
    if button[0] and grab(mouse_pos, red, released, launch):
        create_band(screen, band, (257, 413), attach_point)

    screen.blit(image('images/slingshot/right_stick_sling.png', (300,300)), (75,320))
    red_body.mask(screen, red) 

    if button[0] and grab(mouse_pos, red, released, launch):
        create_band(screen, band, (197, 418), attach_point)

    screen.blit(image('images/slingshot/left_stick_sling.png', (300,300)), (75, 320))
    pig_b.mask(screen, pig)

    for body, box in boxes:
        body.mask(screen, box)

    pygame.display.flip()
    clock.tick(60)
