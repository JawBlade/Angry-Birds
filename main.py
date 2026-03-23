import pygame
import pymunk
import pymunk.pygame_util
import os
from helpers import image, create_band, snap_check, grab
from objects import Box
from characters import Pig, Bird
import math

SLING_POS     = (225, 410)

pygame.display.set_caption('Knock-Off Angry Birds')

width, height = (1280, 720)

pygame.init()
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()
running = True

band = pygame.Surface((10, 20), pygame.SRCALPHA)
band.fill((159, 26, 13))

space = pymunk.Space()
space.gravity = (0,900)
space.damping = 0.65
draw_options = pymunk.pygame_util.DrawOptions(screen)


box_1_body = Box((40, 100), (1125, 517), image_path="images/box.jpeg")
box_1 = box_1_body.create(space)

box_2_body = Box((40, 100), (1000, 517), image_path="images/box.jpeg")
box_2 = box_2_body.create(space)

boxes = [
    [box_1_body, box_1],
    [box_2_body, box_2]
]

# Adds Floor
floor_body = space.static_body
floor_body.position = (0, 567)
floor = pymunk.Segment(floor_body, (0, 0), (1280, 0), 1)
floor.friction = 1
floor.color = (103, 177, 20, 0)
space.add(floor)

red_body = Bird(0.6, 27, (225,410), image_path="images/red2.webp")
red = red_body.create(space)

aim_body = space.static_body
aim = pymunk.Segment(aim_body, (225,410), (red.position[0], red.position[1]), 5)
aim.elasticity = 0.8
aim.sensor = True 
aim.color = (255,0,0,0)
space.add(aim)

pig_b = Pig(1, 27, (1063,540), image_path="images/pig.webp")
pig = pig_b.create(space)

released=False
dragging = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            bird_x, bird_y = red.position
            mouse_x, mouse_y = event.pos
            dist = math.hypot(bird_x - mouse_x, bird_y - mouse_y) 
            if dist < 40:
                dragging = True
                released = False

            if grab(pygame.mouse.get_pos(), red, released):
                is_dragging = True

        if event.type == pygame.MOUSEBUTTONUP: 
            if dragging:
                dragging = False
                released = True
                px, py = red.position
                offset_x = 225 - px
                offset_y = 410 - py
                POWER = 12
                red.body_type = pymunk.Body.DYNAMIC
                red.velocity = (offset_x * POWER, offset_y * POWER)

    button = pygame.mouse.get_pressed()
    if dragging:
            # Move bird with mouse, clamped to pull radius
            mx, my = pygame.mouse.get_pos()
            dx, dy = mx - SLING_POS[0], my - SLING_POS[1]
            dist = math.hypot(dx, dy)
            if dist > 90:
                dx, dy = dx * 90/dist, dy * 90/dist
                # Set position directly — no velocity zeroing
                red.position = (SLING_POS[0] + dx, SLING_POS[1] + dy)
                red.velocity = (0, 0)   # keep still while held
                red.angular_velocity = 0
                last_pull_pos = red.position

            elif not released:
                # Sitting on sling untouched
                red.position = SLING_POS
                red.velocity = (0, 0)

    MAX_VEL = 3000
    for body in space.bodies:
        if body.body_type == pymunk.Body.DYNAMIC:
            vx, vy = body.velocity
            if math.isnan(vx) or math.isnan(vy):
                body.velocity = (0, 0)
                body.angular_velocity = 0
                body.position = (body.position.x or 0, body.position.y or 0)
            else:
                speed = body.velocity.length
                if speed > MAX_VEL:
                    body.velocity = body.velocity * (MAX_VEL / speed)

    released = snap_check(red, released) 
    space.step(1.0 / 60.0)

    screen.blit(image('images/back.jpg', (width, height)), (0,0))
    
    x, y = red.position
    dx, dy = x - 225, y - 410 
    angle_to_bird = math.atan2(dy, dx)
    attach_point = (x + math.cos(angle_to_bird) * 36, y + math.sin(angle_to_bird) * 36)

    if button[0] and grab(pygame.mouse.get_pos(), red, released):
        create_band(screen, band, (257, 413), attach_point)

    screen.blit(image('images/slingshot/right_stick_sling.png', (300,300)), (75,320))
    red_body.mask(screen, red) 

    if button[0] and grab(pygame.mouse.get_pos(), red, released):
        create_band(screen, band, (197, 418), attach_point)

    screen.blit(image('images/slingshot/left_stick_sling.png', (300,300)), (75, 320))
    pig_b.mask(screen, pig)

    for body, box in boxes:
        body.mask(screen, box)

    pygame.display.flip()
    clock.tick(60)
