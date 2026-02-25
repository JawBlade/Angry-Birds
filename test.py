import pygame
import pymunk
import math

# --- Configuration ---
WIDTH, HEIGHT = 600, 600
FPS = 60

# 1. Initialize Pygame and Pymunk
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
space = pymunk.Space()
space.gravity = (0, 900)  # Gravity pulls down

# 2. Create the Physics Square
# body_type Dynamic means it moves and reacts to gravity
mass = 1
size = 50
moment = pymunk.moment_for_box(mass, (size, size))
body = pymunk.Body(mass, moment)
body.position = (300, 100) # Start in the middle-top

shape = pymunk.Poly.create_box(body, (size, size))
shape.elasticity = 0.8  # Bounciness
space.add(body, shape)

# 3. Create a static floor so the box doesn't fall forever
floor_body = space.static_body
floor_shape = pymunk.Segment(floor_body, (0, 550), (600, 550), 5)
floor_shape.elasticity = 0.8
space.add(floor_shape)

# 4. Load the Image
# Replace "logo.png" with your image file path
# We scale it to match the 'size' of our physics box
img_original = pygame.Surface((size, size)) 
#img_original.fill((255, 100, 100)) # Placeholder: Red square if no image loaded
img_original = pygame.image.load("images/box.jpeg").convert_alpha()
# img_original = pygame.transform.scale(img_original, (size, size))

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255)) # Clear screen

    # --- Step 1: Physics ---
    dt = 1.0 / FPS
    space.step(dt)

    # --- Step 2: Rendering the Image ---
    # Get physics position
    x, y = body.position
    
    # Pymunk uses Radians, Pygame uses Degrees
    # We use negative angle because Pygame rotates counter-clockwise
    angle_degrees = math.degrees(-body.angle)

    # Rotate the image
    img_rotated = pygame.transform.rotate(img_original, angle_degrees)
    
    # Important: Center the image on the physics body
    # Rotating an image changes its width/height, so we must re-center it
    rect = img_rotated.get_rect(center=(x, y))

    # Draw to screen
    screen.blit(img_rotated, rect.topleft)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
