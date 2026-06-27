import os
import math
import pymunk
import pygame


def image(path : str, size : tuple, alpha=True):
    if not alpha:    
        img = pygame.image.load(os.path.join(path)).convert()
    else:
        img =  pygame.image.load(os.path.join(path)).convert_alpha()
        
    img = pygame.transform.scale(img, size)

    return img

class Box:
    def __init__(self, size: tuple, pos: tuple, image_path: str = None, image_surf: pygame.Surface = None, health= 175):
        self.size = size
        self.pos = pos
        self._image_original = None
        self._cached_img     = None
        self.health = health

        if image_surf is not None:
            self._image_original = image_surf
        elif image_path:
            self._image_original = pygame.image.load(image_path).convert_alpha()

    def create(self, space):
        # Make the rigid Body
        body = pymunk.Body(mass=0.7, moment=500)

        body.position = self.pos

        box = pymunk.Poly.create_box(body, self.size, radius=2)
        box.collision_type = 2
        box.friction = 0.8
        box.elasticity = 0.0

        space.add(body, box)
        
        return body

    # Gemini did the masking for the boxes.
    def mask(self, screen, body):
        # Render the image centered on the physics body
        x, y = body.position

        if self._image_original:
            if self._cached_img is None or self._cached_img.get_size() != (int(self.size[0]), int(self.size[1])):
                self._cached_img = pygame.transform.smoothscale(self._image_original, (int(self.size[0]), int(self.size[1])))
            img = self._cached_img
        else:
            img = pygame.Surface((int(self.size[0]), int(self.size[1])), pygame.SRCALPHA)
            img.fill((150, 75, 0, 255))

        angle_degrees = math.degrees(-body.angle)
        img_rotated = pygame.transform.rotate(img, angle_degrees)
        rect = img_rotated.get_rect(center=(int(x), int(y)))

        screen.blit(img_rotated, rect.topleft)
    
    def remove(self, body, space):
        shapes = list(body.shapes)
        for shape in shapes:
            if shape in space.shapes:
                space.remove(shape)
        if body in space.bodies:
            space.remove(body)