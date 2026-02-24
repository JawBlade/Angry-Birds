import pygame 
import os

def image(path : str, size : tuple, alpha=True):
    if not alpha:    
        img = pygame.image.load(os.path.join(path)).convert()
    else:
        img =  pygame.image.load(os.path.join(path)).convert_alpha()
        
    img = pygame.transform.scale(img, size)

    return img