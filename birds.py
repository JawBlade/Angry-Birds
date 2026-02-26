import pymunk
import pygame
import math 

class bird:
    def _init__(self, mass : int, radius : int, pos : tuple):
        self.mass = mass
        self.radius = radius
        self.pos = pos


    def create(self, space):
        mass = 10
        radius = 25

        moment = pymunk.moment_for_circle(mass, 0, radius)

        body = pymunk.Body(mass, moment)
        body.position = self.pos

        circle = pymunk.Circle(body, radius)

        space.add(body, circle)

        return body, circle