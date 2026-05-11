import os
import math
from tkinter import font
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

        self.WIDTH, self.HEIGHT = (self.game.WIDTH, self.game.HEIGHT)
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

        floor_body = self.space.static_body
        floor_body.position = (0, 567)
        floor = pymunk.Segment(floor_body, (-1000, 0), (2280, 0), 1)
        floor.friction = 1
        floor.color = (103, 177, 20, 0)
        self.space.add(floor)

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
        bird_x, bird_y = self.red.position
        self.mouse_pos = pygame.mouse.get_pos()

        if self.dragging:
            self.idle = False
            dx, dy = self.mouse_pos[0] - self.SLING_POS[0], self.mouse_pos[1] - self.SLING_POS[1]
            dist = math.hypot(dx, dy)
            if dist > self.MAX_PULL:
                dx = dx * self.MAX_PULL / dist
                dy = dy * self.MAX_PULL / dist
            self.red.position = (self.SLING_POS[0] + dx, self.SLING_POS[1] + dy)
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
        elif bird_x >= 1300 and bird_y >= 500:
            if self.released:
                self.LIVES -= 1
            self.released, self.dragging, self.idle, self.launch = respawn(self.red, self.LIVES)

        clamp_vels(self.space)
        self.space.step(1.0 / 60.0)

        dx, dy = bird_x - 225, bird_y - 410
        angle_to_bird = math.atan2(dy, dx)
        self.attach_point = (bird_x + math.cos(angle_to_bird) * 36, bird_y + math.sin(angle_to_bird) * 36)

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

# I got help creating the Button from claude.
class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.bg_img = image('images/back.jpg', (1280, 720))

        self.growing = True
        self.growth = 0

        self.font_size = 44
        self.menu = True
        
        self.GOLD_DARK  = (210, 140,  10)
        self.GOLD_MID   = (240, 175,  20)
        self.GOLD_LIGHT = (255, 210,  80)
        self.CREAM      = (255, 245, 210)
        self.RADIUS     = 18

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game.running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_rect.collidepoint(event.pos):

                if self.menu == False:
                    self.game.change_state(PlayingState(self.game))

                self.menu = False

    def update(self):
        if self.growing:
            self.growth += 0.4
            self.font_size += 0.2
            if self.growth >= 20:
                self.growing = False
        else:
            self.growth -= 0.4
            self.font_size -= 0.2
            if self.growth <= 0:
                self.growing = True

        if self.menu == False:
            BTN_W, BTN_H = 75 + self.growth , 90 + self.growth
        elif self.menu:
            BTN_W, BTN_H = 212 + self.growth, 90 + self.growth

        self.btn_rect = pygame.Rect((1280 - BTN_W) // 2, (720 - BTN_H) // 2, BTN_W, BTN_H)

        self.btn_font = pygame.font.Font('../angrybirds-regular.ttf', int(self.font_size))

    def draw(self, screen):
        if self.menu:
            screen.blit(self.bg_img, (0, 0))

            self.text_surf   = self.btn_font.render("LEVELS", True, (255, 255, 255))
            self.shadow_surf = self.btn_font.render("LEVELS", True, (180, 140, 30))
            text_surface = self.game.font.render("Angry Birds", True, (0, 0, 0))
            screen.blit(text_surface, (425, 100))

            self._draw_button(screen)
        elif self.menu == False:
            screen.blit(self.bg_img, (0, 0))

            self.text_surf   = self.btn_font.render("1", True, (255, 255, 255))
            self.shadow_surf = self.btn_font.render("1", True, (180, 140, 30))
            text_surface = self.game.font.render("Angry Birds", True, (0, 0, 0))
            screen.blit(text_surface, (self.game.WIDTH // 2 - text_surface.get_width() // 2, 100))

            self._draw_button(screen)

        pygame.display.flip()
        self.game.clock.tick(60)

    def _draw_button(self, surf):
        r = self.btn_rect
        RADIUS = self.RADIUS

        pygame.draw.rect(surf, self.GOLD_DARK, r, border_radius=RADIUS)

        inner = r.inflate(-6, -6)
        pygame.draw.rect(surf, self.GOLD_MID, inner, border_radius=RADIUS - 2)

        rim = inner.inflate(-6, -6)
        pygame.draw.rect(surf, self.CREAM, rim, border_radius=RADIUS - 4)

        fill = rim.inflate(-8, -8)
        pygame.draw.rect(surf, self.GOLD_MID, fill, border_radius=RADIUS - 6)

        tx = r.centerx - self.text_surf.get_width() // 2
        ty = r.centery - self.text_surf.get_height() // 2 - 2
        for dx, dy in [(-2, 2), (2, 2), (0, 3), (-2, -1), (2, -1)]:
            surf.blit(self.shadow_surf, (tx + dx, ty + dy))
        surf.blit(self.text_surf, (tx, ty))
    
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
    