import pygame 
import math
import os
import pymunk


def image(path : str, size : tuple, alpha=True):
    if not alpha:    
        img = pygame.image.load(os.path.join(path)).convert()
    else:
        img =  pygame.image.load(os.path.join(path)).convert_alpha()
        
    img = pygame.transform.scale(img, size)

    return img

def respawn(red, screen):

    pygame.transform.rotate(screen, math.degrees(90))
    red.velocity = (0, 0)
    red.angular_velocity = 0
    red.angle = 0
    red.position = (225, 410)
    
    return False, False, True, False

def distance(p1, p2):
    return math.sqrt((p2[1] - p1[1]) **2 + (p2[0] - p1[0]) **2)

# Checks if you let go of the bird in a certain radius
def snap_check(red, released : bool, SLINGSHOT_POS=(225, 410)):
    SNAP_RADIUS = 60
    if released and red.velocity.length < 5:
        dist = distance(red.position, SLINGSHOT_POS)

        if dist < SNAP_RADIUS:
            red.position = SLINGSHOT_POS
            red.velocity = (0,0)
            return False
    return released

# Checks if you click close enough to the bird
def grab(mouse_pos : tuple, red, released : bool, launch : bool):
    SNAP_RADIUS = 40
    if not released and not launch:
        bird_x, bird_y = red.position
        dx = bird_x - mouse_pos[0]
        dy = bird_y - mouse_pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance < SNAP_RADIUS:
            red.position = pygame.mouse.get_pos()
            red.velocity = (0,0)
            red.angular_velocity = 0
            return True
    return False

# Gemini did this
def create_band(screen, img, start_pos : tuple, end_pos : tuple):

    x1, y1 = start_pos
    x2, y2 = end_pos

    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(-angle_rad)

    if dist > 1:
        stretched_img = pygame.transform.scale(img, (int(dist), 20))
        
        rotated_img = pygame.transform.rotate(stretched_img, angle_deg)
        
        midpoint = ((x1 + x2) / 2, (y1 + y2) / 2)
        rect = rotated_img.get_rect(center=midpoint)
        screen.blit(rotated_img, rect)

        perp_angle = angle_rad + math.pi / 2
        half_thick = 20 / 2
        
        off_x = math.cos(perp_angle) * half_thick
        off_y = math.sin(perp_angle) * half_thick

        points = [
            (x1 + off_x, y1 + off_y), 
            (x2 + off_x, y2 + off_y), 
            (x2 - off_x, y2 - off_y), 
            (x1 - off_x, y1 - off_y) 
        ]
        
        pygame.draw.polygon(screen, (0, 0, 0), points, 2)


 # Clause did this
def clamp_vels(space):
    MAX_VEL = 3000
    for body in space.bodies:
        if body.body_type == pymunk.Body.DYNAMIC:
            vx, vy = body.velocity
            if math.isnan(vx) or math.isnan(vy):
                body.velocity = (0, 0)
                body.angular_velocity = 0
            else:
                speed = body.velocity.length
                if speed > MAX_VEL:
                    body.velocity = body.velocity * (MAX_VEL / speed)

from objects import Box

# Adds all the boxes within the array of boxes in our space/level
def make_box(size : tuple, pos : tuple, space, image_path="images/box.jpeg"):
    body = Box(size, pos, image_path=image_path)
    return [body, body.create(space)]