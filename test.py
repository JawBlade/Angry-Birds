import pygame
import pymunk

# --- Setup ---
pygame.init()
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()
space = pymunk.Space()
space.gravity = (0, 900)

# 1. THE FLOOR (Category 1)
# We want everything to hit the floor.
floor_body = space.static_body
floor_shape = pymunk.Segment(floor_body, (0, 380), (600, 380), 5)
floor_shape.filter = pymunk.ShapeFilter(categories=0b1) # Category 1
space.add(floor_shape)

# 2. THE BALL (Category 2)
# We want the ball to hit the floor (Category 1)
ball_body = pymunk.Body(1, 100)
ball_body.position = (300, 50)
ball_shape = pymunk.Circle(ball_body, 20)
# Mask=0b1 means "Only collide with Category 1"
ball_shape.filter = pymunk.ShapeFilter(categories=0b10, mask=0b1) 
space.add(ball_body, ball_shape)

# 3. THE GHOST BOX (Category 4)
# We make this a SENSOR so it doesn't affect the ball physically
ghost_body = pymunk.Body(body_type=pymunk.Body.STATIC)
ghost_body.position = (300, 200)
ghost_shape = pymunk.Poly.create_box(ghost_body, (100, 50))
ghost_shape.sensor = True  # <--- THIS makes it not affect others
space.add(ghost_body, ghost_shape)

# --- Main Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    space.step(1/60.0)
    screen.fill((240, 240, 240)) # Light Gray background

    # --- Draw the Floor ---
    pygame.draw.line(screen, (34, 139, 34), (0, 380), (600, 380), 5)

    # --- Draw the Ghost Box (Blue) ---
    # Since it's a sensor, the ball will pass through it!
    pygame.draw.rect(screen, (0, 100, 255, 100), (250, 175, 100, 50), 2)

    # --- Draw the Ball (Red) ---
    pos = ball_body.position
    pygame.draw.circle(screen, (200, 50, 50), (int(pos.x), int(pos.y)), 20)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()