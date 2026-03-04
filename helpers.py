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

def create_band(screen, start : tuple, end : tuple):

    x, y = start
    
    ex, ey = end

    pygame.draw.line(screen, (154, 25, 11), (x, y), (ex - 33, ey + 10), 20)
    pygame.draw.line(screen, (0,0,0), (x, y - 11), (ex - 33, ey), 3)
    pygame.draw.line(screen, (0,0,0), (x, y + 9), (ex - 33, ey + 20), 3)