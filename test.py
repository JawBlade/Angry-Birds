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