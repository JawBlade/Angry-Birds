import os
import math
from tkinter import font
import pygame
import pymunk
from objects import image, Box
import pymunk.pygame_util
from characters import Pig, Bird
from helpers import create_band, snap_check, grab, make_box, respawn, clamp_vels
import time

class State:
    def __init__(self, game):
        self.game = game

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass

    # func to help create a button
    def draw_button(self, surf, rect, text, font_size=int(44), icon_path=None):
        
        self.GOLD_DARK  = (210, 140,  10)
        self.GOLD_MID   = (240, 175,  20)
        self.GOLD_LIGHT = (255, 210,  80)
        self.CREAM      = (255, 245, 210)

        font = pygame.font.Font('angrybirds/angrybirds-regular.ttf', font_size)
        self.level_rect = rect
        self.text_surf = font.render(text, True, (255, 255, 255))
        self.shadow_surf = font.render(text, True, (180, 140, 30))
        
        r = self.level_rect
        RADIUS = 18

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

        # Claude Did this for me
        if icon_path:
            icon = pygame.image.load(icon_path).convert_alpha()
            # Scale to fit inside the button with some padding
            icon_size = min(rect.height - 20, rect.width - 20)
            icon = pygame.transform.smoothscale(icon, (icon_size, icon_size))
            icon_rect = icon.get_rect(center=rect.center)
            surf.blit(icon, icon_rect)
        else:
            # your existing text drawing code
            tx = r.centerx - self.text_surf.get_width() // 2
            ty = r.centery - self.text_surf.get_height() // 2 - 2
            for dx, dy in [(-2, 2), (2, 2), (0, 3), (-2, -1), (2, -1)]:
                surf.blit(self.shadow_surf, (tx + dx, ty + dy))
            surf.blit(self.text_surf, (tx, ty))

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

        self.space.on_collision(1, 2, post_solve=self.on_hit) # Handles the collision between bird and boxes.

        self.space.on_collision(2, 3, post_solve=self.on_hit) # Handles the collision between boxes and pigs.

        self.space.on_collision(1, 3, post_solve=self.on_hit) # Handles collisions between birds and pigs.

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

        right_wall = pymunk.Segment(self.space.static_body, (1280, -1000), (1280, 1000), 1)
        right_wall.friction = 1
        self.space.add(right_wall)

        left_wall = pymunk.Segment(self.space.static_body, (0, -1000), (0, 1000), 1)
        left_wall.friction = 1
        self.space.add(left_wall)

        # Setting up the bird, rubber band and pigs.
        self.red_body = Bird(0.6, 27, (225, 410), image_path="images/red2.webp")
        self.red = self.red_body.create(self.space)

        self.band = pygame.Surface((10, 20), pygame.SRCALPHA)
        self.band.fill((159, 26, 13))

        self.pig_b = Pig(1, 27, (1063, 540), image_path="images/pig.webp")
        self.pig = self.pig_b.create(self.space)

        # Normal vars for logic.
        self.released = False
        self.mouse_pos = (0, 0)
        self.dragging = False
        self.idle = True
        self.launch = False
        self.MAX_PULL = 120
        self.SLING_POS = (225, 410)
        self.LIVES = 3

        #Pause Button 
        #                                x  y   W   H
        self.Pause_Button = pygame.Rect(20, 12, 65, 65)

        # Shows how many lives u got.
        self.life_display = []
        for i in range(self.LIVES -1):
            life_counter = image('images/red2.webp', (64, 64))
            self.life_display.append(life_counter)

        self.bg_img = image('images/back.jpg', (self.WIDTH, self.HEIGHT))
        self.sling_r = image('images/slingshot/right_stick_sling.png', (300, 300))
        self.sling_l = image('images/slingshot/left_stick_sling.png', (300, 300))

        # Fliping the values bc i named them wrong
        self.entities = {}
        self.entities[self.pig] = self.pig_b
        for box_obj, box_body in self.boxes:
            self.entities[box_body] = box_obj

        
        self.start_time = time.perf_counter() # To add a Higher score if you finsh the level faster.
        self.score = 0

    # This handles like all the inputs for the game.
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game.running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            # Checking if the bird if slow enough to respawn and if it was launched.
            if self.red.velocity.length <= 75:
                if self.released:
                    self.LIVES -= 1
                self.released, self.dragging, self.idle, self.launch = respawn(self.red, self.LIVES)

            bird_x, bird_y = self.red.position
            mouse_x, mouse_y = event.pos
            dist = math.hypot(bird_x - mouse_x, bird_y - mouse_y)

            # Mouse has to be close enough to drag and hasn't been launched.
            if dist < 40 and not self.launch:
                self.dragging = True
                self.released = False

            if grab(self.mouse_pos, self.red, self.released, self.launch):
                self.dragging = True

            # For the Pause button
            if self.Pause_Button.collidepoint(event.pos):
                print(self.score)
                self.game.change_state(PausedState(self.game, self))

        if event.type == pygame.MOUSEBUTTONUP:

            # Logic that launches the bird.
            if self.dragging and not self.launch:
                self.dragging = False
                self.released = True
                px, py = self.red.position
                offset_x = 225 - px
                offset_y = 410 - py
                POWER = 12
                self.red.body_type = pymunk.Body.DYNAMIC
                self.red.velocity = (offset_x * POWER, offset_y * POWER)

    # Updates all the vars that need to be updated and some logic.
    def update(self):
        bird_x, bird_y = self.red.position
        self.mouse_pos = pygame.mouse.get_pos()

        # The main big if statement that handles the dragging and launching of the bird.
        if self.dragging:
            self.idle = False
            dx, dy = self.mouse_pos[0] - self.SLING_POS[0], self.mouse_pos[1] - self.SLING_POS[1]
            dist = math.hypot(dx, dy)

            # This sets the radus of how far we can pull back.
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

        # If the bird is off screen, respawn the bird.
        elif (bird_x >= 1300 and bird_y >= 500) or (bird_x <= -400 and bird_y >= -1300) :
            if self.released:
                self.LIVES -= 1
            self.released, self.dragging, self.idle, self.launch = respawn(self.red, self.LIVES)

        clamp_vels(self.space) # Forgot what this does but Ik it's important.

        # Logic that switches sprites
        for body, obj in self.entities.items():
            if obj.health is not None and obj.health <= 50:
                if isinstance(obj, Box):
                    obj._image_original = pygame.image.load('images/box_50hp.jpeg').convert_alpha()
                    obj._cached_img = None
                elif isinstance(obj, Pig):
                    obj._image_original = pygame.image.load('images/50hp_pig.webp').convert_alpha()
                    obj._cached_img = None

        dead = [body for body, obj in self.entities.items() if obj.health is not None and obj.health <= 0]
        
        # Actually get rid of them on screen.
        for body in dead:
            obj = self.entities[body]

            #Increases score when box breaks or pig dies
            if type(obj).__name__ == 'Pig':
                self.score += 3000
            elif type(obj).__name__ == 'Box':
                self.score += 1000
            
            self.entities[body].remove(body, self.space)
            self.boxes = [[obj, b] for obj, b in self.boxes if b != body]
            del self.entities[body]
            
        self.space.step(1.0 / 60.0)

        dx, dy = bird_x - 225, bird_y - 410
        angle_to_bird = math.atan2(dy, dx)
        self.attach_point = (bird_x + math.cos(angle_to_bird) * 36, bird_y + math.sin(angle_to_bird) * 36)
    
    # Draws all the visuals
    def draw(self, screen):
        screen.blit(self.bg_img, (0, 0))

        # lives
        gap = 100
        for i in range(min(self.LIVES - 1, len(self.life_display))):
            screen.blit(self.life_display[i], (gap, 10))
            gap += 70
        
        self.draw_button(screen, self.Pause_Button, "II", font_size=35) # Pause button

        if self.dragging:
            create_band(screen, self.band, (257, 413), self.attach_point)

        screen.blit(self.sling_r, (75, 320))
        self.red_body.mask(screen, self.red)

        if self.dragging:
            create_band(screen, self.band, (197, 418), self.attach_point)

        screen.blit(self.sling_l, (75, 320))
        if self.pig in self.entities:
            self.pig_b.mask(screen, self.pig)

        for body, box in self.boxes:
            body.mask(screen, box)

    # Checks if the impules is above a threshold to damget eh obj based on the impulse.
    def on_hit(self, arbiter, space, data):
        impulse = arbiter.total_impulse.length
        THRESHOLD = 30

        if impulse > THRESHOLD:
            damage = impulse * 0.5

            for shape in arbiter.shapes:
                body = shape.body

                if body in self.entities:
                    self.entities[body].health -= damage

        return True

# I got help creating the Button from claude.
class MenuState(State):
    def __init__(self, game):
        super().__init__(game)
        self.bg_img = image('images/back.jpg', (1280, 720))

        self.growing = True
        self.growth = 0

        self.font_size = 44
        self.menu = True

    # Checks what buttons are being pressed and what to do when they are
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game.running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.level_1_rect.collidepoint(event.pos):

                if self.menu == False:
                    self.game.change_state(PlayingState(self.game))

                self.menu = False
            elif self.back_rect.collidepoint(event.pos):
                if self.menu == False:
                    self.game.change_state(MenuState(self.game))


    def update(self):
        # The logic to animate the play button
        if self.growing:
            self.growth += 0.4
            if self.menu:
                self.font_size += 0.2
            if self.growth >= 20:
                self.growing = False
        else:
            self.growth -= 0.4
            if self.menu:
                self.font_size -= 0.2
            if self.growth <= 0:
                self.growing = True

        if self.menu:
            BTN_W, BTN_H = 212 + self.growth, 90 + self.growth
        elif self.menu == False:
            BTN_W, BTN_H = (75 , 90)

        # Need to make a rect for each button
        self.level_rect = pygame.Rect((1280 - BTN_W) // 2, (720 - BTN_H) // 2, BTN_W, BTN_H)
        self.level_1_rect = pygame.Rect((1280 - BTN_W) // 2, (720 - BTN_H) // 2, BTN_W, BTN_H)
        self.back_rect = pygame.Rect(20, 20, BTN_W + 20, BTN_H - 20)


        self.level_font = pygame.font.Font('C:/Users/vicbe/OneDrive/Desktop/Projects/Angry-Birds/angrybirds/angrybirds-regular.ttf', int(self.font_size))
        self.back_font = pygame.font.Font('C:/Users/vicbe/OneDrive/Desktop/Projects/Angry-Birds/angrybirds/angrybirds-regular.ttf', int(20))


    # Drawing all the visuals for the menu
    def draw(self, screen):
        if self.menu:
            screen.blit(self.bg_img, (0, 0))

            self.draw_button(screen, self.level_rect, "LEVELS") # Level button

            # The Title
            text_surface = self.game.font.render("Angry Birds", True, (0, 0, 0))
            screen.blit(text_surface, (self.game.WIDTH // 2 - text_surface.get_width() // 2, 100))

        elif self.menu == False: 

            # Background
            screen.blit(self.bg_img, (0, 0))

            self.draw_button(screen, self.level_1_rect, "1") # Level 1

            self.draw_button(screen, self.back_rect, "BACK", 25) # back button

            text_surface = self.game.font.render("Angry Birds", True, (0, 0, 0))
            screen.blit(text_surface, (self.game.WIDTH // 2 - text_surface.get_width() // 2, 100))


class PausedState(State):
    def __init__(self, game, previous_playing_state):
        super().__init__(game)

        self.previous_state = previous_playing_state
        
        self.WIDTH, self.HEIGHT = (self.game.WIDTH, self.game.HEIGHT)
        self.screen = self.game.screen
        self.clock = self.game.clock

        # Button Rects
        self.Play_Button    = pygame.Rect(60, 10, 85, 85) # Play
        self.Restart_Button = pygame.Rect(130, 170, 85, 85) # restart
        self.Level_Button   = pygame.Rect(130, 350, 85, 85) # Level Menu

        self.invis_rect = pygame.Surface((300, self.HEIGHT))
        self.invis_rect.fill((17,17,132))
        self.invis_rect.set_alpha(200)

        self.invis_rect_back = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.invis_rect_back.fill((0,0,0))
        self.invis_rect_back.set_alpha(150)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game.running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            
            if self.Play_Button.collidepoint(event.pos):
                self.game.change_state(self.previous_state)

            elif self.Restart_Button.collidepoint(event.pos):
                self.game.change_state(PlayingState(self.game))

            elif self.Level_Button.collidepoint(event.pos):
                paused = MenuState(self.game)
                
                paused.menu = False
                self.game.change_state(paused)

        if event.type == pygame.MOUSEBUTTONUP:
            pass

    def draw(self, screen):
        self.previous_state.draw(screen)

        screen.blit(self.invis_rect_back, (0,0))
        screen.blit(self.invis_rect, (0,0))

        self.draw_button(screen, self.Play_Button, "", font_size=35, icon_path="images/play-button.png")
        self.draw_button(screen, self.Restart_Button, "", font_size=35, icon_path="images/arrow-outline.png")
        self.draw_button(screen, self.Level_Button, "", font_size=35, icon_path="images/hamburger.png")

        pygame.display.flip()
        self.clock.tick(60)
    
class GameoverState(State):
    def __init__(self, game):
        super().__init__(game)

    def handle_event(self, event):
        pass

    def update(self):
        pass

    def draw(self, screen):
        pass
    