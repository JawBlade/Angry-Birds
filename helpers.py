import pygame 
import math
import os

def image(path : str, size : tuple, alpha=True):
    if not alpha:    
        img = pygame.image.load(os.path.join(path)).convert()
    else:
        img =  pygame.image.load(os.path.join(path)).convert_alpha()
        
    img = pygame.transform.scale(img, size)

    return img

def calc(p1, p2):
    return math.sqrt((p2[1] - p1[1]) **2 + (p2[0] - p1[0]) **2)

def calc_angle(p1, p2):
    return math.atan2(p2[1] - p1[1], p2[0] - p1[0])

def snap_check(red, released, SLINGSHOT_POS=(225, 410)):
    SNAP_RADIUS = 60
    if released:
        bird_x, bird_y = red.position
        dx = bird_x - SLINGSHOT_POS[0]
        dy = bird_y - SLINGSHOT_POS[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance < SNAP_RADIUS:
            # We teleport the physics body
            red.position = SLINGSHOT_POS
            red.velocity = (0,0)
            red.angular_velocity = 0
            return False
    return released

def grab(mouse_pos, red, released):
    SNAP_RADIUS = 40
    if not released:
        bird_x, bird_y = red.position
        dx = bird_x - mouse_pos[0]
        dy = bird_y - mouse_pos[1]
        distance = math.sqrt(dx**2 + dy**2)

        if distance < SNAP_RADIUS:
            red.position = pygame.mouse.get_pos()
            red.velocity = (0,0)
            red.angular_velocity = 0
            return True


# Gemini did this
def create_band(screen, img, start_pos, end_pos):

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