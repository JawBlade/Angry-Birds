import pymunk
import pygame
import math 

class bird:
    def __init__(self, mass : int, radius : int, pos : tuple, image_path: str = None, image_surf: pygame.Surface = None):
        self.mass = mass
        self.radius = radius
        self.pos = pos
        self._cached_img = None 
        self._image_original = None

        if image_surf is not None:
            self._image_original = image_surf
        elif image_path:
            self._image_original = pygame.image.load(image_path).convert_alpha()


    def create(self, space):
        mass = self.mass
        radius = self.radius

        moment = pymunk.moment_for_circle(mass, 0, radius)

        body = pymunk.Body(mass, moment)
        body.position = self.pos

        circle = pymunk.Circle(body, radius)
        circle.friction = 1
        
        space.add(body, circle)

        return body

    # Gemini pretty much implemented all the image stuff for the birds. 
    # I do understand how it works tho.
    def mask(self, screen, body):
        x, y = body.position
        
        diameter = int(self.radius * 2.7)

        if self._image_original:
            if self._cached_img is None:
                self._cached_img = pygame.transform.smoothscale(self._image_original, (diameter, diameter))
            img = self._cached_img
        else:
            img = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            pygame.draw.circle(img, (255, 0, 0), (self.radius, self.radius), self.radius)

        angle_degrees = math.degrees(-body.angle)
        img_rotated = pygame.transform.rotate(img, angle_degrees)
        offset = (-7, -5)
        world_pos = body.local_to_world(offset)
        rect = img_rotated.get_rect(center=(int(world_pos.x), int(world_pos.y)))
        screen.blit(img_rotated, rect)