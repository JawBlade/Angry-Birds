import math
from tkinter import font
import pygame
import pymunk
from objects import image, Box
import pymunk.pygame_util
from characters import Pig, Bird
from helpers import create_band, snap_check, grab, make_box, respawn, clamp_vels
from levels import LEVELS
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
    def __init__(self, game, level_num=1):
        super().__init__(game)

        self.level_num = level_num
        level_data = LEVELS[level_num]

        self.WIDTH, self.HEIGHT = (self.game.WIDTH, self.game.HEIGHT)
        self.screen = self.game.screen
        self.clock = self.game.clock

        self.space = pymunk.Space()
        self.space.gravity = (0, 900)
        self.space.damping = 0.65
        self.space.iterations = 30 
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        self.space.on_collision(1, 2, post_solve=self.on_hit) # Handles the collision between bird and boxes.

        self.space.on_collision(2, 3, post_solve=self.on_hit) # Handles the collision between boxes and pigs.

        self.space.on_collision(1, 3, post_solve=self.on_hit) # Handles collisions between birds and pigs.

        self.boxes = [
            make_box(b["size"], b["pos"], self.space)
            for b in level_data["boxes"]
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
        self.red_body = Bird(1, 27, (225, 410), image_path="images/red2.webp")
        self.red = self.red_body.create(self.space)

        self.band = pygame.Surface((10, 20), pygame.SRCALPHA)
        self.band.fill((159, 26, 13))

        self.pigs = []
        for p in level_data["pigs"]:
            pig_b = Pig(p["mass"], p["radius"], p["pos"], image_path="images/pig.webp")
            pig = pig_b.create(self.space)
            self.pigs.append((pig_b, pig))

        # Normal vars for logic.
        self.released = False
        self.mouse_pos = (0, 0)
        self.dragging = False
        self.idle = True
        self.launch = False
        self.MAX_PULL = 120
        self.SLING_POS = (225, 410)
        self.LIVES = level_data["lives"]
        self.end = False
        self.show_end_button = False

        #Pause Button 
        #                                x  y   W   H
        self.Pause_Button = pygame.Rect(20, 12, 65, 65)

        self.End_Button = pygame.Rect(self.game.WIDTH - 160, self.game.HEIGHT - 70, 150, 60)

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
        for pig_b, pig in self.pigs:
            self.entities[pig] = pig_b
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
                self.game.change_state(PausedState(self.game, self))
            elif self.show_end_button and self.End_Button.collidepoint(event.pos):
                self.show_end_button = False
                self.game.change_state(GameoverState(self.game, self))

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

        self.pig_count = sum(1 for obj in self.entities.values() if isinstance(obj, Pig))

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

        if self.pig_count == 0 or self.LIVES == 0:
            self.show_end_button = True

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

        dt = 1.0 / 60.0
        steps = 3
        for _ in range(steps):
            self.space.step(dt / steps)

        dx, dy = bird_x - 225, bird_y - 410
        angle_to_bird = math.atan2(dy, dx)
        self.attach_point = (bird_x + math.cos(angle_to_bird) * 36, bird_y + math.sin(angle_to_bird) * 36)

    # Draws all the visuals
    def draw(self, screen):
        screen.blit(self.bg_img, (0, 0))

        if self.show_end_button:
            self.draw_button(screen, self.End_Button, "END LEVEL", font_size=30)

        # lives
        gap = 100
        for i in range(min(self.LIVES - 1, len(self.life_display))):
            screen.blit(self.life_display[i], (gap, 10))
            gap += 70

        # Display Score
        text_surface = self.game.font.render(str(self.score), True, (0, 0, 0))
        self.screen.blit(text_surface, (self.game.WIDTH - 210, 0))

        self.draw_button(screen, self.Pause_Button, "II", font_size=35) # Pause button

        if self.dragging:
            create_band(screen, self.band, (257, 413), self.attach_point)

        screen.blit(self.sling_r, (75, 320))
        self.red_body.mask(screen, self.red)

        if self.dragging:
            create_band(screen, self.band, (197, 418), self.attach_point)

        screen.blit(self.sling_l, (75, 320))
        for pig_b, pig in self.pigs:
            if pig in self.entities:
                pig_b.mask(screen, pig)

        for body, box in self.boxes:
            body.mask(screen, box)

    # Checks if the impules is above a threshold to damget eh obj based on the impulse.
    def on_hit(self, arbiter, space, data):
        impulse = arbiter.total_impulse.length
        THRESHOLD = 30

        if impulse > THRESHOLD:
            damage = impulse * 0.45

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

        # Build one rect per level in LEVELS
        self.level_count = len(LEVELS)
        self.level_rects = []

    # Checks what buttons are being pressed and what to do when they are
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game.running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.menu:
                if self.level_1_rect.collidepoint(event.pos):
                    self.menu = False
            else:
                # Check each level button
                for i, rect in enumerate(self.level_rects):
                    if rect.collidepoint(event.pos):
                        level_num = i + 1
                        if level_num == 1 or (level_num - 1) in self.game.completed_levels:
                            self.game.change_state(PlayingState(self.game, level_num=level_num))
                        return
                if self.back_rect.collidepoint(event.pos):
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

        # Build rects for each level button, laid out in a row centred on screen
        BTN_SIZE = 75
        GAP = 20
        total_width = self.level_count * BTN_SIZE + (self.level_count - 1) * GAP
        start_x = (1280 - total_width) // 2
        self.level_rects = [
            pygame.Rect(start_x + i * (BTN_SIZE + GAP), (720 - BTN_SIZE) // 2, BTN_SIZE, BTN_SIZE)
            for i in range(self.level_count)
        ]

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

            # Draw a button for each level
            for i, rect in enumerate(self.level_rects):
                self.draw_button(screen, rect, str(i + 1))
                level_num = i + 1
                if level_num != 1 and (level_num - 1) not in self.game.completed_levels:
                    dim = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    dim.fill((0, 0, 0, 120))
                    screen.blit(dim, rect.topleft)

            self.draw_button(screen, self.back_rect, "BACK", 25) # back button

            text_surface = self.game.font.render("Angry Birds", True, (0, 0, 0))
            screen.blit(text_surface, (self.game.WIDTH // 2 - text_surface.get_width() // 2, 100))


# I had claude make a better looking menu for the pause and game over state but i programmed 
# all the logic i also descreiibed exaclty how i wanted the menu. I just didnt want to waste 
# time on programming it myself, when I knew claude could do it.
class PausedState(State):
    def __init__(self, game, previous_playing_state):
        super().__init__(game)

        self.previous_state = previous_playing_state
        
        self.WIDTH, self.HEIGHT = (self.game.WIDTH, self.game.HEIGHT)
        self.screen = self.game.screen
        self.clock = self.game.clock

        panel_w, panel_h = 400, 350
        self.panel_rect = pygame.Rect(
            (self.WIDTH - panel_w) // 2,
            (self.HEIGHT - panel_h) // 2,
            panel_w, panel_h
        )

        btn_y = self.panel_rect.bottom - 110
        btn_size = 85
        spacing = 110
        center_x = self.WIDTH // 2

        self.Play_Button    = pygame.Rect(center_x - spacing - btn_size // 2, btn_y, btn_size, btn_size)
        self.Restart_Button = pygame.Rect(center_x - btn_size // 2,           btn_y, btn_size, btn_size)
        self.Level_Button   = pygame.Rect(center_x + spacing - btn_size // 2, btn_y, btn_size, btn_size)

        self.invis_rect_back = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.invis_rect_back.fill((0, 0, 0))
        self.invis_rect_back.set_alpha(150)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game.running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.Play_Button.collidepoint(event.pos):
                self.game.change_state(self.previous_state)
            elif self.Restart_Button.collidepoint(event.pos):
                self.game.change_state(PlayingState(self.game, level_num=self.previous_state.level_num))
            elif self.Level_Button.collidepoint(event.pos):
                paused = MenuState(self.game)
                paused.menu = False
                self.game.change_state(paused)

    def draw(self, screen):
        self.previous_state.draw(screen)

        screen.blit(self.invis_rect_back, (0, 0))

        pygame.draw.rect(screen, (17, 17, 132), self.panel_rect, border_radius=20)
        pygame.draw.rect(screen, (255, 210, 80), self.panel_rect, width=4, border_radius=20)

        title_font = pygame.font.Font('angrybirds/angrybirds-regular.ttf', 52)
        title = title_font.render("PAUSED", True, (255, 210, 80))
        screen.blit(title, (self.panel_rect.centerx - title.get_width() // 2, self.panel_rect.top + 40))

        self.draw_button(screen, self.Play_Button,    "", font_size=35, icon_path="images/play-button.png")
        self.draw_button(screen, self.Restart_Button, "", font_size=35, icon_path="images/arrow-outline.png")
        self.draw_button(screen, self.Level_Button,   "", font_size=35, icon_path="images/hamburger.png")

        pygame.display.flip()
        self.clock.tick(60)

class GameoverState(State):
    def __init__(self, game, previous_playing_state):
        super().__init__(game)

        self.previous_state = previous_playing_state
        self.level_num = previous_playing_state.level_num
        self.pig_count = previous_playing_state.pig_count
        
        self.WIDTH, self.HEIGHT = (self.game.WIDTH, self.game.HEIGHT)
        self.screen = self.game.screen
        self.clock = self.game.clock

        self.invis_rect_back = pygame.Surface((self.WIDTH, self.HEIGHT))
        self.invis_rect_back.fill((0, 0, 0))
        self.invis_rect_back.set_alpha(150)

        # Central panel
        panel_w, panel_h = 500, 350
        self.panel_rect = pygame.Rect(
            (self.WIDTH - panel_w) // 2,
            (self.HEIGHT - panel_h) // 2,
            panel_w, panel_h
        )

        btn_y = self.panel_rect.bottom - 110
        btn_size = 85
        spacing = 130
        center_x = self.WIDTH // 2

        self.Level_Button   = pygame.Rect(center_x - spacing - btn_size // 2, btn_y, btn_size, btn_size)
        self.Restart_Button = pygame.Rect(center_x - btn_size // 2,           btn_y, btn_size, btn_size)
        self.Play_Button    = pygame.Rect(center_x + spacing - btn_size // 2, btn_y, btn_size, btn_size)

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.game.running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.Play_Button.collidepoint(event.pos):
                if self.pig_count == 0:
                    self.game.completed_levels.add(self.level_num)
                    next_level = self.level_num + 1
                    if next_level in LEVELS:
                        self.game.change_state(PlayingState(self.game, level_num=next_level))
                    else:
                        menu = MenuState(self.game)
                        menu.menu = False
                        self.game.change_state(menu)
                else:
                    self.game.change_state(PlayingState(self.game, level_num=self.level_num))

            elif self.Restart_Button.collidepoint(event.pos):
                self.game.change_state(PlayingState(self.game, level_num=self.level_num))

            elif self.Level_Button.collidepoint(event.pos):
                menu = MenuState(self.game)
                menu.menu = False
                self.game.change_state(menu)

    def draw(self, screen):
        self.previous_state.draw(screen)
        screen.blit(self.invis_rect_back, (0, 0))

        pygame.draw.rect(screen, (17, 17, 132), self.panel_rect, border_radius=20)
        pygame.draw.rect(screen, (255, 210, 80), self.panel_rect, width=4, border_radius=20)

        score_font = pygame.font.Font('angrybirds/angrybirds-regular.ttf', 52)
        label_font = pygame.font.Font('angrybirds/angrybirds-regular.ttf', 28)

        label = label_font.render("SCORE", True, (255, 210, 80))
        score = score_font.render(str(self.previous_state.score + self.previous_state.LIVES * 500), True, (255, 255, 255))
        screen.blit(label, (self.panel_rect.centerx - label.get_width() // 2, self.panel_rect.top + 30))
        screen.blit(score, (self.panel_rect.centerx - score.get_width() // 2, self.panel_rect.top + 70))

        # Pigs still alive message
        if self.pig_count > 0:
            msg_font = pygame.font.Font('angrybirds/angrybirds-regular.ttf', 22)
            msg = msg_font.render("All pigs need to die to pass the level!", True, (255, 80, 80))
            screen.blit(msg, (self.panel_rect.centerx - msg.get_width() // 2, self.panel_rect.top + 145))

        self.draw_button(screen, self.Level_Button,   "", font_size=35, icon_path="images/hamburger.png")
        self.draw_button(screen, self.Restart_Button, "", font_size=35, icon_path="images/arrow-outline.png")
        self.draw_button(screen, self.Play_Button,    "", font_size=35, icon_path="images/play-button.png")

        pygame.display.flip()
        self.clock.tick(60)