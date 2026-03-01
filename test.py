import pygame
import pymunk

class PhysicsObject:
    """The Parent: Handles all the Pymunk body/shape setup."""
    def __init__(self, space, pos, radius, mass, color):
        self.color = color
        self.radius = radius
        
        # 1. Create Pymunk Physics
        moment = pymunk.moment_for_circle(mass, 0, radius)
        self.body = pymunk.Body(mass, moment)
        self.body.position = pos
        self.shape = pymunk.Circle(self.body, radius)
        self.shape.elasticity = 0.5
        self.shape.friction = 0.5
        space.add(self.body, self.shape)

    def draw(self, screen):
        # Convert Pymunk coordinates to Pygame coordinates
        pos = int(self.body.position.x), int(self.body.position.y)
        pygame.draw.circle(screen, self.color, pos, int(self.radius))

class Bird(PhysicsObject):
    """The Child: Inherits everything, but we can add 'Bird' logic."""
    def __init__(self, space, pos):
        # Birds are Red and heavy
        super().__init__(space, pos, radius=15, mass=5, color=(255, 0, 0))
    
    def launch(self, impulse):
        self.body.apply_impulse_at_local_point(impulse)

class Pig(PhysicsObject):
    """The Child: Inherits everything, but we can add 'Pig' logic."""
    def __init__(self, space, pos):
        # Pigs are Green and lighter
        super().__init__(space, pos, radius=12, mass=2, color=(0, 255, 0))

def create_floor(space):
    # Static body stays in place forever
    body = space.static_body
    shape = pymunk.Segment(body, (0, 380), (800, 380), 10)
    shape.elasticity = 0.4
    shape.friction = 1.0
    space.add(shape)
    return shape

# --- Setup Game ---
pygame.init()
screen = pygame.display.set_mode((800, 400))
space = pymunk.Space()
space.gravity = (0, 900)

create_floor(space) # Add the floor to the physics world
entities = [Bird(space, (150, 100)), Pig(space, (600, 300))]

# --- Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False

    space.step(1/60.0)
    screen.fill((255, 255, 255))

    # Draw Floor
    pygame.draw.line(screen, (50, 50, 50), (0, 380), (800, 380), 10)

    # Draw Entities
    for ent in entities:
        ent.draw(screen)

    pygame.display.flip()
    pygame.time.Clock().tick(60)

pygame.quit()