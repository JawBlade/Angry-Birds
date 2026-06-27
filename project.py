import math
import pygame
from states import PlayingState, MenuState, PausedState, GameoverState


# ── The three required top-level functions ────────────────────────────────────
# These live here to satisfy CS50P requirements

def distance(p1: tuple, p2: tuple) -> float:
    """Return the Euclidean distance between two (x, y) points."""
    return math.sqrt((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2)


def snap_check(red, released: bool, SLINGSHOT_POS=(225, 410)) -> bool:
    """
    If the bird has been released and is within SNAP_RADIUS of the slingshot,
    snap it back and cancel the release. Returns the new value of `released`.
    """
    SNAP_RADIUS = 45
    if released:
        dist = distance(red.position, SLINGSHOT_POS)
        if dist < SNAP_RADIUS:
            red.position = SLINGSHOT_POS
            red.velocity = (0, 0)
            return False
    return released


def grab(mouse_pos: tuple, red, released: bool, launch: bool) -> bool:
    """
    Return True if the mouse is close enough to the bird to grab it,
    and the bird hasn't already been released or launched.
    """
    GRAB_RADIUS = 40
    if not released and not launch:
        dist = distance(red.position, mouse_pos)
        if dist < GRAB_RADIUS:
            return True
    return False


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    pygame.init()
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SRCALPHA)
    clock = pygame.time.Clock()

    # Reuse the Game class from main.py to avoid duplicating anything
    from main import Game
    game = Game()
    game.run()


if __name__ == "__main__":
    main()