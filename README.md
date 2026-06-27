# Angry Birds (Knock-off)
#### Video Demo: https://youtu.be/5fEJoUKW7wM
#### Description:

## What is this project?

This is a knock-off Angry Birds game built in Python using Pygame and Pymunk. The player uses a slingshot to launch birds at structures made of wooden boxes, with the goal of killing all the pigs on screen. The game features a full menu system, multiple levels of increasing difficulty, a scoring system, pause and game over screens, and physics-based collision and destruction.

## Screenshots

**Main Menu**

![Main Menu](start.png)

**Level Select**

![Level Select](images\screenshots\menu.png)

**Gameplay**

![Gameplay](play.png)

## How to run it

Install the dependencies first:

```
pip install -r requirements.txt
```

Then launch the game:

```
python project.py
```

## Files

### `project.py`
This is the main entry point required by CS50P. It contains the `main()` function which starts the game, as well as three top-level functions required by the course: `distance`, `snap_check`, and `grab`. These functions handle core slingshot logic — calculating how far the bird is from a point, checking whether the bird should snap back to the slingshot when released too close, and determining whether the player's mouse is close enough to grab the bird. The rest of the game runs through the `Game` class in `main.py`.

### `main.py`
Contains the `Game` class which initializes Pygame, sets the screen size, manages the game clock, and holds the state machine that switches between the menu, playing, paused, and game over screens. It also loads the custom Angry Birds font used throughout the UI.

### `states.py`
This is the largest and most important file in the project. It defines four game states:

- **`PlayingState`** — the core gameplay loop. It sets up the Pymunk physics space, spawns the bird, boxes, and pigs based on the current level, handles all mouse input for dragging and launching the bird, updates physics each frame, checks for destroyed objects and removes them, tracks score, manages lives, and draws everything to the screen including the slingshot rubber band effect.
- **`MenuState`** — the main menu and level select screen. It shows an animated "LEVELS" button on the main screen, and a grid of level buttons when the player clicks it. Levels are locked until the previous one is completed.
- **`PausedState`** — an overlay that pauses the game and shows buttons to resume, restart, or go back to the level select.
- **`GameoverState`** — shown when the level ends. Displays the player's score and buttons to go to the next level, restart, or go back to the menu. If pigs are still alive, the player cannot advance.

### `characters.py`
Defines the `characters` base class and two subclasses: `Bird` and `Pig`. Each character has a mass, radius, position, and health. The `create` method adds the character to the Pymunk physics space as a circle with the correct collision type. The `mask` method handles drawing the character's image on screen, rotated to match the physics body's angle. The `remove` method cleanly removes the body and its shapes from the space when it dies.

### `objects.py`
Defines the `Box` class which represents the wooden blocks that make up the structures. Each box has a size, position, image, and health. It uses `pymunk.Poly.create_box` to create a rectangular physics body. Like characters, it has a `mask` method for drawing and a `remove` method for cleanup.

### `helpers.py`
Contains utility functions used across the game: `make_box` to spawn a box into the space, `respawn` to reset the bird after each shot, `distance` to calculate Euclidean distance between two points, `snap_check` to snap the bird back if released too close to the slingshot, `grab` to check if the mouse is close enough to pick up the bird, `create_band` to draw the stretched rubber band effect, and `clamp_vels` to prevent physics bodies from reaching unrealistic speeds.

### `levels.py`
A dictionary that defines all 5 levels. Each level specifies the number of lives, the positions and sizes of boxes, and the positions, masses, and radii of pigs. Adding a new level is as simple as adding a new entry to this dictionary — no other code needs to change.

### `test_project.py`
Contains 12 pytest tests covering the three top-level functions in `project.py`. The tests use a lightweight `FakeBody` class to simulate a Pymunk body without needing a display or physics space, so they run instantly from the command line with `pytest test_project.py`.

### `requirements.txt`
Lists the two pip-installable dependencies: `pygame` for rendering, input, and audio, and `pymunk` for 2D rigid body physics.

## Design decisions

One key decision was keeping the CS50P-required top-level functions (`distance`, `snap_check`, `grab`) in `project.py` while leaving identical versions in `helpers.py` as well. This avoids breaking any of the existing game code that imports from `helpers.py`, meaning none of the original files needed to be changed to satisfy the course requirements.

The physics are handled entirely by Pymunk, with collision handlers set up between three collision types: birds (type 1), boxes (type 2), and pigs (type 3). When two objects collide, the impulse of the collision is used to calculate damage. Objects below 50% health switch to a damaged sprite, and objects that reach 0 health are removed from the space and added to the score.

The slingshot mechanic works by clamping the bird's position to a maximum pull radius from the slingshot center while the player is dragging. On mouse release, the offset between the bird and the slingshot origin is multiplied by a power constant and applied as the launch velocity, simulating the elastic band snapping forward.

Level progression is tracked in a `completed_levels` set on the `Game` object, so levels stay unlocked for the whole session even if the player navigates back to the menu.