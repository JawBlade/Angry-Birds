import pygame
import math

# --- Setup ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Assets ---
band_img = pygame.Surface((10, 20), pygame.SRCALPHA)
band_img.fill((200, 50, 50))

def draw_stretchy_band(surface, base_img, start_pos, end_pos):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx, dy = x2 - x1, y2 - y1
    dist = math.hypot(dx, dy)
    angle_rad = math.atan2(dy, dx)
    
    if dist > 1:
        stretched = pygame.transform.scale(base_img, (int(dist), 20))
        rotated = pygame.transform.rotate(stretched, math.degrees(-angle_rad))
        rect = rotated.get_rect(center=((x1 + x2) / 2, (y1 + y2) / 2))
        surface.blit(rotated, rect)
        
        # Black border
        perp = angle_rad + math.pi/2
        off_x, off_y = math.cos(perp) * 10, math.sin(perp) * 10
        pts = [(x1+off_x, y1+off_y), (x2+off_x, y2+off_y), (x2-off_x, y2-off_y), (x1-off_x, y1-off_y)]
        pygame.draw.polygon(surface, (0, 0, 0), pts, 2)

# --- Main Logic ---
anchor_left = (350, 350)
anchor_right = (450, 350)
circle_radius = 35
running = True

while running:
    screen.fill((50, 50, 50))
    mouse_pos = pygame.mouse.get_pos()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # 1. Calculate the angle from the slingshot to the circle
    center_sling = (400, 350)
    dx = mouse_pos[0] - center_sling[0]
    dy = mouse_pos[1] - center_sling[1]
    angle_to_circle = math.atan2(dy, dx)

    # 2. THE FLIP: Add the radius instead of subtracting it
    # This pushes the attachment point to the OPPOSITE side (the front)
    front_x = mouse_pos[0] + math.cos(angle_to_circle) * circle_radius
    front_y = mouse_pos[1] + math.sin(angle_to_circle) * circle_radius
    attach_point = (front_x, front_y)

    # 3. DRAWING ORDER (Layers)
    
    # Layer 1: Back Band (starts from right anchor)
    draw_stretchy_band(screen, band_img, anchor_right, attach_point)

    # Layer 2: The Circle (Drawing this in the middle makes the bands look like they wrap)
    pygame.draw.circle(screen, (200, 50, 50), mouse_pos, circle_radius)
    pygame.draw.circle(screen, (0, 0, 0), mouse_pos, circle_radius, 3)

    # Layer 3: Front Band (starts from left anchor)
    draw_stretchy_band(screen, band_img, anchor_left, attach_point)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()