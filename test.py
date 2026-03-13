import pygame

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((400, 400))

# 1. Define the invisible clickable area
snap_boundary = pygame.draw.circle(screen, (255,255,255), (200,200), 100, 0) # x, y, width, height
is_hidden = True

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # 2. Check for the click
        if event.type == pygame.MOUSEBUTTONUP:
            if snap_boundary.collidepoint(event.pos):
                print("You found the secret button!")
                is_hidden = False # Reveal it once clicked

    screen.fill((30, 30, 30)) # Dark background

    # 3. Only draw if it's NOT hidden
    if not is_hidden:
        pygame.draw.circle(screen, (255,255,255), (200,200), 100, 0)
        

    pygame.display.flip()





    # Before the loop
released = False
is_grabbing = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if mouse is clicking near the bird
            if math.hypot(event.pos[0] - red.position.x, event.pos[1] - red.position.y) < 30:
                is_grabbing = True
                red.body_type = pymunk.Body.STATIC

        if event.type == pygame.MOUSEBUTTONUP:
            if is_grabbing:
                is_grabbing = False
                released = True
                red.body_type = pymunk.Body.DYNAMIC
                
                # LAUNCH LOGIC: Apply impulse based on pull distance
                dx = 225 - red.position.x
                dy = 410 - red.position.y
                # Power multiplier (try 15-20)
                red.apply_impulse_at_local_point((dx * 15, dy * 15))

    # Handle Dragging
    if is_grabbing:
        red.position = pygame.mouse.get_pos()
    
    # Check for snapping back to sling if release was too weak
    released = snap_check(red, released)

    # Physics Step
    space.step(1.0 / 60.0)

    # Drawing code remains the same...