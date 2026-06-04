import pygame

pygame.init()
screen = pygame.display.set_mode((600, 400))
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    screen.fill((100, 200, 100))  # green background

    overlay = pygame.Surface((200, 200))
    overlay.fill((0, 0, 255))
    overlay.set_alpha(100)
    screen.blit(overlay, (200, 100))

    pygame.display.flip()
    clock.tick(60)