import os
import math
import pygame
import pymunk
from objects import image
import pymunk.pygame_util
from characters import Pig, Bird
from helpers import create_band, snap_check, grab, make_box, respawn, clamp_vels, distance


# This is just Boiler Plate
pygame.display.set_caption('Knock-Off Angry Birds')

pygame.init()

WIDTH, HEIGHT = (1280, 720)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock  = pygame.time.Clock()

space = pymunk.Space()
space.gravity = (0,900)
space.damping = 0.65
draw_options  = pymunk.pygame_util.DrawOptions(screen)

# Make the different boxes for the level
boxes = [
    make_box((40, 100), (1125, 517), space),
    make_box((40, 100), (1000, 517), space),
]

# Adds Floor
floor_body = space.static_body
floor_body.position = (0, 567)
floor = pymunk.Segment(floor_body, (-1000, 0), (2280, 0), 1)
floor.friction = 1
floor.color    = (103, 177, 20, 0)
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
MAX_PULL  = 120
SLING_POS = (225, 410)
LIVES     = 3

life_display = []
for i in range(LIVES):
    life_counter = image('images/red2.webp', (64,64))
    life_display.append(life_counter)

bg_img  = image('images/back.jpg', (WIDTH, HEIGHT))
sling_r = image('images/slingshot/right_stick_sling.png', (300,300))
sling_l = image('images/slingshot/left_stick_sling.png', (300,300))

while running:
    bird_x, bird_y = red.position
    mouse_pos      = pygame.mouse.get_pos()

    # Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if red.velocity.length <= 75:
                if released == True:
                    LIVES -= 1
                released, dragging, idle, launch = respawn(red, LIVES)

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
                px, py   = red.position
                offset_x = 225 - px
                offset_y = 410 - py
                POWER = 12
                red.body_type = pymunk.Body.DYNAMIC
                red.velocity  = (offset_x * POWER, offset_y * POWER)

    button = pygame.mouse.get_pressed()
    # Logic for different states
    if dragging:
        idle   = False
        dx, dy = mouse_pos[0] - SLING_POS[0], mouse_pos[1] - SLING_POS[1]
        dist   = math.hypot(dx, dy)
        if dist > MAX_PULL:
            dx = dx * MAX_PULL / dist
            dy = dy * MAX_PULL / dist
        red.position = (SLING_POS[0] + dx, SLING_POS[1] + dy)
        red.velocity = (0, 0)
        red.angular_velocity = 0
    elif idle:
        red.position = SLING_POS
        red.velocity = (0, 0)
    elif released and not launch:
        released = snap_check(red, released)
        launch   = True

    if launch and red.velocity.length <= 5:
        if released == True:
            LIVES -= 1
        released, dragging, idle, launch = respawn(red, LIVES)
    elif bird_x >= 1300 and  bird_y >= 500:
        if released == True:
            LIVES -= 1
        released, dragging, idle, launch = respawn(red, LIVES)

    clamp_vels(space)
    space.step(1.0 / 60.0)
    
    dx, dy = bird_x - 225, bird_y - 410 
    angle_to_bird = math.atan2(dy, dx)
    attach_point = (bird_x + math.cos(angle_to_bird) * 36, bird_y + math.sin(angle_to_bird) * 36)

    # Drawing Logic like the visuals: Bakcgroud, bird, pig, Slingshot, and boxes
    screen.blit(bg_img, (0, 0))

    gap = 10
    for i in range(LIVES):
        screen.blit(life_display[i], (gap, 10))
        gap += 70

    if dragging:
        create_band(screen, band, (257, 413), attach_point)
            
    screen.blit(sling_r, (75, 320))
    red_body.mask(screen, red) 

    if dragging:
        create_band(screen, band, (197, 418), attach_point)
            
    screen.blit(sling_l, (75, 320))
    pig_b.mask(screen, pig)

    for body, box in boxes:
        body.mask(screen, box)

    pygame.display.flip()
    clock.tick(60)