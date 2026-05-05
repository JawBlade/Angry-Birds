import os
import math
import pygame
import pymunk
from objects import image
import pymunk.pygame_util
from characters import Pig, Bird
from helpers import create_band, snap_check, grab, make_box, respawn, clamp_vels, distance

class State:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass


class PlayingState(State):
    def __init__(self, game):
        super().__init__(game)

        self.WIDTH, self.HEIGHT = (1280, 720)
        self.screen = self.game.screen
        self.clock = self.game.clock

        self.space = pymunk.Space()
        self.space.gravity = (0, 900)
        self.space.damping = 0.65
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        self.boxes = [
            make_box((40, 100), (1125, 517), self.space),
            make_box((40, 100), (1000, 517), self.space),
        ]

        self.floor_body = self.space.static_body
        self.floor_body.position = (0, 567)
        self.floor = pymunk.Segment(self.floor_body, (-1000, 0), (2280, 0), 1)
        self.floor.friction = 1
        self.floor.color = (103, 177, 20, 0)
        self.space.add(self.floor)

        self.red_body = Bird(0.6, 27, (225, 410), image_path="images/red2.webp")
        self.red = self.red_body.create(self.space)

        self.band = pygame.Surface((10, 20), pygame.SRCALPHA)
        self.band.fill((159, 26, 13))

        self.pig_b = Pig(1, 27, (1063, 540), image_path="images/pig.webp")
        self.pig = self.pig_b.create(self.space)

        self.released = False
        self.mouse_pos = (0, 0)
        self.dragging = False
        self.idle = True
        self.launch = False
        self.MAX_PULL = 120
        self.SLING_POS = (225, 410)
        self.LIVES = 3

        self.life_display = []
        for i in range(self.LIVES):
            life_counter = image('images/red2.webp', (64, 64))
            self.life_display.append(life_counter)

        self.bg_img = image('images/back.jpg', (self.WIDTH, self.HEIGHT))
        self.sling_r = image('images/slingshot/right_stick_sling.png', (300, 300))
        self.sling_l = image('images/slingshot/left_stick_sling.png', (300, 300))

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game.running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.red.velocity.length <= 75:
                if self.released:
                    self.LIVES -= 1
                self.released, self.dragging, self.idle, self.launch = respawn(self.red, self.LIVES)

            bird_x, bird_y = self.red.position
            mouse_x, mouse_y = event.pos
            dist = math.hypot(bird_x - mouse_x, bird_y - mouse_y)
            if dist < 40 and not self.launch:
                self.dragging = True
                self.released = False

            if grab(self.mouse_pos, self.red, self.released, self.launch):
                self.dragging = True

        if event.type == pygame.MOUSEBUTTONUP:
            if self.dragging and not self.launch:
                self.dragging = False
                self.released = True
                px, py = self.red.position
                offset_x = 225 - px
                offset_y = 410 - py
                POWER = 12
                self.red.body_type = pymunk.Body.DYNAMIC
                self.red.velocity = (offset_x * POWER, offset_y * POWER)

    def update(self):
        self.bird_x, self.bird_y = self.red.position
        self.mouse_pos = pygame.mouse.get_pos()
        self.button = pygame.mouse.get_pressed()

        if self.dragging:
            self.idle = False
            self.dx, self.dy = self.mouse_pos[0] - self.SLING_POS[0], self.mouse_pos[1] - self.SLING_POS[1]
            self.dist = math.hypot(self.dx, self.dy)
            if self.dist > self.MAX_PULL:
                self.dx = self.dx * self.MAX_PULL / self.dist
                self.dy = self.dy * self.MAX_PULL / self.dist
            self.red.position = (self.SLING_POS[0] + self.dx, self.SLING_POS[1] + self.dy)
            self.red.velocity = (0, 0)
            self.red.angular_velocity = 0
        elif self.idle:
            self.red.position = self.SLING_POS
            self.red.velocity = (0, 0)
        elif self.released and not self.launch:
            self.released = snap_check(self.red, self.released)
            self.launch = True

        if self.launch and self.red.velocity.length <= 5:
            if self.released:
                self.LIVES -= 1
            self.released, self.dragging, self.idle, self.launch = respawn(self.red, self.LIVES)
        elif self.bird_x >= 1300 and self.bird_y >= 500:
            if self.released:
                self.LIVES -= 1
            self.released, self.dragging, self.idle, self.launch = respawn(self.red, self.LIVES)

        clamp_vels(self.space)
        self.space.step(1.0 / 60.0)

        self.dx, self.dy = self.bird_x - 225, self.bird_y - 410
        self.angle_to_bird = math.atan2(self.dy, self.dx)
        self.attach_point = (self.bird_x + math.cos(self.angle_to_bird) * 36, self.bird_y + math.sin(self.angle_to_bird) * 36)

    def draw(self, screen):
        screen.blit(self.bg_img, (0, 0))

        gap = 10
        for i in range(self.LIVES):
            screen.blit(self.life_display[i], (gap, 10))
            gap += 70

        if self.dragging:
            create_band(screen, self.band, (257, 413), self.attach_point)

        screen.blit(self.sling_r, (75, 320))
        self.red_body.mask(screen, self.red)

        if self.dragging:
            create_band(screen, self.band, (197, 418), self.attach_point)

        screen.blit(self.sling_l, (75, 320))
        self.pig_b.mask(screen, self.pig)

        for body, box in self.boxes:
            body.mask(screen, box)

        pygame.display.flip()
        self.clock.tick(60)


class MenuState(State):
    def __init__(self, game):
        super().__init__(game)

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass
    
class PausedState(State):
    def __init__(self, game):
        super().__init__(game)

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass
    
class GameoverState(State):
    def __init__(self, game):
        super().__init__(game)

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass
    