import pymunk
import pygame
from helpers import image
import math


class Box:
    def __init__(self, size: tuple, pos: tuple, image_path: str = None, image_surf: pygame.Surface = None):
        self.size = size
        self.pos = pos
        self._image_original = None
        self._cached_img = None

        if image_surf is not None:
            self._image_original = image_surf
        elif image_path:
            self._image_original = pygame.image.load(image_path).convert_alpha()

    def create(self, space):
        # Make the rigid Body
        body = pymunk.Body(mass=0.2, moment=10)

        body.position = self.pos

        # Create a Box
        box = pymunk.Poly.create_box(body, self.size, radius=2)

        space.add(body, box)
        
        return body

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