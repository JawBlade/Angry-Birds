import pygame

# --- Configuration ---
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60
CAPTION = 'My Pygame Game'

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(CAPTION)
clock = pygame.time.Clock()

visible = 1

# --- Main Game Loop ---
running = True
while running:
    # 1. Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Add other event handling (e.g., keyboard/mouse input) here

    # 2. Game logic and updates
    # Add game object updates here

    # 3. Drawing
    if visible == 2:
        circle = pygame.draw.circle(screen, (255,255,255), (200,200), 100, 0)
                                    
    screen.fill((0, 0, 0)) # Fill the screen with black (RGB)

    # Add drawing commands for game objects here

    # 4. Update the display
    pygame.display.flip() # or pygame.display.update()

    # 5. Cap the frame rate
    clock.tick(FPS)

# --- Quit Pygame ---
pygame.quit()
