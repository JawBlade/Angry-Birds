import pygame
import pymunk
import pymunk.pygame_util

def create_circle(space, pos, radius=20):
    """Creates a dynamic circle in the physics space."""
    mass = 1
    inertia = pymunk.moment_for_circle(mass, 0, radius)
    body = pymunk.Body(mass, inertia)
    body.position = pos
    
    shape = pymunk.Circle(body, radius)
    shape.elasticity = 0.8  # Makes it bouncy
    shape.friction = 0.5
    
    space.add(body, shape)
    return shape

def create_floor(space):
    """Creates a static line that objects can land on."""
    body = space.static_body 
    floor = pymunk.Segment(body, (0, 550), (800, 550), 5)
    floor.elasticity = 0.8
    floor.friction = 0.5
    space.add(floor)
    return floor

def main():
    # --- Initialize Pygame ---
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # --- Initialize Pymunk ---
    space = pymunk.Space()
    space.gravity = (0, 900)  # Gravity (x, y)

    # Create the floor
    create_floor(space)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Create a circle wherever the user clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                create_circle(space, event.pos)

        # --- Physics & Drawing ---
        screen.fill((255, 255, 255)) # White background
        
        # Step the simulation forward (1/60th of a second)
        space.step(1/60.0)
        
        # Pymunk's helper draws everything in the space for us
        space.debug_draw(draw_options)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
