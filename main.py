import pygame
from states import PlayingState, MenuState, PausedState, GameoverState

class Game:
    def __init__(self):
        pygame.init()
        self.WIDTH, self.HEIGHT = (1280, 720)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        
        self.state = MenuState(self)

        self.font = pygame.font.Font('../angrybirds-regular.ttf', 90)

    def change_state(self, new_state):
        self.state = new_state

    def run(self):
        while self.running:
            for event in pygame.event.get():
                self.state.handle_event(event)
            self.state.update()
            self.state.draw(self.screen)

if __name__ == "__main__":
    game = Game()
    game.run()