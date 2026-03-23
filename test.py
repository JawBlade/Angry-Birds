import pygame
import pymunk
import math
from helpers import image, create_band, snap_check
from objects import Box
from characters import Pig, Bird

WIDTH, HEIGHT = 1280, 720
SLING_POS     = (225, 410)
FLOOR_Y       = 567
MAX_VEL       = 3000

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Knock-Off Angry Birds – Level 1")
clock      = pygame.time.Clock()
font_big   = pygame.font.SysFont("monospace", 52, bold=True)
font_small = pygame.font.SysFont("monospace", 24)

band_surf = pygame.Surface((10, 20), pygame.SRCALPHA)
band_surf.fill((159, 26, 13))


def build_level(space):
    boxes, pigs = [], []

    for pos in [(980, 511), (1060, 511)]:
        b = Box((30, 110), pos, image_path="images/box.jpeg")
        boxes.append([b, b.create(space)])
    b = Box((110, 28), (1020, 451), image_path="images/box.jpeg")
    boxes.append([b, b.create(space)])
    p = Pig(1, 27, (1020, 418), image_path="images/pig.webp")
    pigs.append([p, p.create(space)])

    for pos in [(1170, 527), (1170, 447)]:
        b = Box((38, 80), pos, image_path="images/box.jpeg")
        boxes.append([b, b.create(space)])
    p = Pig(1, 27, (1170, 400), image_path="images/pig.webp")
    pigs.append([p, p.create(space)])

    p = Pig(1, 27, (870, 538), image_path="images/pig.webp")
    pigs.append([p, p.create(space)])

    return boxes, pigs


def clamp_vels(space):
    for body in space.bodies:
        if body.body_type == pymunk.Body.DYNAMIC:
            vx, vy = body.velocity
            if math.isnan(vx) or math.isnan(vy):
                body.velocity = (0, 0)
                body.angular_velocity = 0
            else:
                spd = body.velocity.length
                if spd > MAX_VEL:
                    body.velocity = body.velocity * (MAX_VEL / spd)


def draw_overlay(text, sub, color):
    ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 160))
    screen.blit(ov, (0, 0))
    t  = font_big.render(text, True, color)
    t2 = font_small.render(sub, True, (220, 220, 220))
    screen.blit(t,  (WIDTH//2 - t.get_width()//2,  HEIGHT//2 - 60))
    screen.blit(t2, (WIDTH//2 - t2.get_width()//2, HEIGHT//2 + 10))


def spawn_bird(space):
    bd = Bird(0.6, 27, SLING_POS, image_path="images/red2.webp")
    b  = bd.create(space)
    b.body_type = pymunk.Body.DYNAMIC
    b.velocity  = (0, 0)
    return bd, b


def run_level():
    space = pymunk.Space()
    space.gravity = (0, 900)
    space.damping = 0.65

    floor = pymunk.Segment(space.static_body, (0, 0), (WIDTH, 0), 1)
    floor.friction = 1
    space.static_body.position = (0, FLOOR_Y)
    space.add(floor)

    boxes, pigs = build_level(space)

    bird_obj, red = spawn_bird(space)
    birds_left = 2

    released   = False
    dragging   = False
    score      = 0
    state      = "playing"
    dead_pigs  = set()
    rest_timer = 0

    # track last pull position so we can compute launch velocity
    last_pull_pos = SLING_POS

    running = True
    while running:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:      return "restart"
                if event.key == pygame.K_ESCAPE: return "quit"

            if state != "playing":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return "restart"
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                bx, by = red.position
                mx, my = event.pos
                if math.hypot(bx - mx, by - my) < 40:
                    dragging = True
                    released = False

            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if dragging:
                    dragging = False
                    released = True
                    # Compute pull offset from sling center and launch
                    px, py = red.position
                    offset_x = SLING_POS[0] - px
                    offset_y = SLING_POS[1] - py
                    POWER = 12
                    red.velocity = (offset_x * POWER, offset_y * POWER)

        if state == "playing":
            if dragging:
                # Move bird with mouse, clamped to pull radius
                mx, my = pygame.mouse.get_pos()
                dx, dy = mx - SLING_POS[0], my - SLING_POS[1]
                dist = math.hypot(dx, dy)
                if dist > 90:
                    dx, dy = dx * 90/dist, dy * 90/dist
                # Set position directly — no velocity zeroing
                red.position = (SLING_POS[0] + dx, SLING_POS[1] + dy)
                red.velocity = (0, 0)   # keep still while held
                red.angular_velocity = 0
                last_pull_pos = red.position

            elif not released:
                # Sitting on sling untouched
                red.position = SLING_POS
                red.velocity = (0, 0)

            # snap back if it barely moved
            released = snap_check(red, released, SLING_POS)

            # pig kill check
            if released:
                bx2, by2 = red.position
                bird_spd = red.velocity.length
                for pig_obj, pig_body in pigs:
                    if id(pig_body) in dead_pigs:
                        continue
                    px, py = pig_body.position
                    if math.hypot(px - bx2, py - by2) < 58 and bird_spd > 300:
                        dead_pigs.add(id(pig_body))
                        score += 500

            # remove dead pigs from space
            for pig_obj, pig_body in pigs:
                if id(pig_body) in dead_pigs:
                    for sh in list(pig_body.shapes):
                        if sh in space.shapes: space.remove(sh)
                    if pig_body in space.bodies: space.remove(pig_body)

            # advance to next bird once current one settles
            if released:
                bx2, by2 = red.position
                off = bx2 > WIDTH + 100 or bx2 < -100 or by2 > FLOOR_Y + 150
                if off or red.velocity.length < 6:
                    rest_timer += 1
                else:
                    rest_timer = 0

                if rest_timer > 40:
                    rest_timer = 0
                    for sh in list(red.shapes):
                        if sh in space.shapes: space.remove(sh)
                    if red in space.bodies: space.remove(red)

                    alive = [p for p in pigs if id(p[1]) not in dead_pigs]
                    if not alive:
                        state  = "win"
                        score += birds_left * 1000
                    elif birds_left > 0:
                        bird_obj, red = spawn_bird(space)
                        birds_left -= 1
                        released = dragging = False
                        last_pull_pos = SLING_POS
                    else:
                        state = "lose"

            alive = [p for p in pigs if id(p[1]) not in dead_pigs]
            if not alive and state == "playing":
                state  = "win"
                score += birds_left * 1000

        clamp_vels(space)
        space.step(1.0 / 60.0)

        # ── draw ──────────────────────────────────────────────────────────────
        screen.blit(image('images/back.jpg', (WIDTH, HEIGHT), alpha=False), (0, 0))

        # trajectory preview
        if dragging:
            bx2, by2 = red.position
            vx = (SLING_POS[0] - bx2) * 12
            vy = (SLING_POS[1] - by2) * 12
            x, y = float(bx2), float(by2)
            for i in range(40):
                x += vx/60; y += vy/60; vy += 900/60
                if y > FLOOR_Y: break
                r = max(2, 5 - i//7)
                pygame.draw.circle(screen, (255, 255, 200), (int(x), int(y)), r)

        bx2, by2  = red.position
        ang       = math.atan2(by2 - SLING_POS[1], bx2 - SLING_POS[0])
        attach_pt = (bx2 + math.cos(ang)*36, by2 + math.sin(ang)*36)
        btn       = pygame.mouse.get_pressed()

        if btn[0] and dragging:
            create_band(screen, band_surf, (257, 413), attach_pt)

        screen.blit(image('images/slingshot/right_stick_sling.png', (300, 300)), (75, 320))
        bird_obj.mask(screen, red)

        if btn[0] and dragging:
            create_band(screen, band_surf, (197, 418), attach_pt)

        screen.blit(image('images/slingshot/left_stick_sling.png', (300, 300)), (75, 320))

        for i in range(min(birds_left, 3)):
            qx = 130 - i * 30
            pygame.draw.circle(screen, (220, 50, 50), (qx, 435), 13)
            pygame.draw.circle(screen, (140, 20, 20), (qx, 435), 13, 2)

        for box_obj, box_body in boxes:
            box_obj.mask(screen, box_body)
        for pig_obj, pig_body in pigs:
            if id(pig_body) not in dead_pigs:
                pig_obj.mask(screen, pig_body)

        sc = font_small.render(f"SCORE  {score}", True, (255, 255, 255))
        bl = font_small.render(f"BIRDS  {birds_left + 1}", True, (255, 220, 80))
        screen.blit(sc, (WIDTH//2 - sc.get_width()//2, 12))
        screen.blit(bl, (18, 12))

        if state == "win":
            draw_overlay("YOU WIN!", f"Score: {score}  —  click or R to replay", (100, 255, 120))
        elif state == "lose":
            draw_overlay("GAME OVER", "Click or R to retry  |  ESC to quit", (255, 80, 80))

        pygame.display.flip()

    return "quit"


result = "restart"
while result == "restart":
    result = run_level()
pygame.quit()