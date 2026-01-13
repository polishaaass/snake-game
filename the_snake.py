"""
Project: "Изгиб Питона" (Snake game).

Classic Snake game implemented with OOP and Pygame.

Rules:
- Snake moves continuously and cannot move backwards instantly.
- When snake eats an apple, it grows by 1 segment.
- Snake wraps through the walls (appears on the opposite side).
- If snake collides with itself, the game resets.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import List, Optional, Tuple

import pygame


# ---------- Constants ----------
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
CELL_SIZE = 20

GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE   # 32
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE  # 24

FPS = 20

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

UP = (0, -CELL_SIZE)
DOWN = (0, CELL_SIZE)
LEFT = (-CELL_SIZE, 0)
RIGHT = (CELL_SIZE, 0)


def wrap_position(position: Tuple[int, int]) -> Tuple[int, int]:
    """
    Wrap a position through the walls.

    Args:
        position: (x, y) position in pixels.

    Returns:
        Wrapped position in pixels.
    """
    x, y = position
    return x % SCREEN_WIDTH, y % SCREEN_HEIGHT


@dataclass
class GameObject:
    """
    Base class for game objects.

    Attributes:
        position: Object position (top-left) in pixels aligned to the grid.
        body_color: RGB color tuple.
    """

    position: Tuple[int, int]
    body_color: Tuple[int, int, int]

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the object on the given surface.

        Must be overridden in subclasses.
        """
        raise NotImplementedError("Subclasses must implement draw().")


class Apple(GameObject):
    """
    Apple that appears on random grid cell.
    """

    def __init__(self) -> None:
        super().__init__(position=(0, 0), body_color=RED)

    def randomize_position(self, forbidden: List[Tuple[int, int]]) -> None:
        """
        Set a new random position for the apple, not colliding with forbidden cells.

        Args:
            forbidden: List of positions that are not allowed (snake cells).
        """
        while True:
            x = random.randrange(0, GRID_WIDTH) * CELL_SIZE
            y = random.randrange(0, GRID_HEIGHT) * CELL_SIZE
            if (x, y) not in forbidden:
                self.position = (x, y)
                return

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the apple on the screen.
        """
        rect = pygame.Rect(self.position[0], self.position[1], CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(surface, self.body_color, rect)


class Snake(GameObject):
    """
    Snake controlled by the player.

    Snake is stored as a list of positions (top-left pixel coords) of segments.
    """

    def __init__(self) -> None:
        center_x = (GRID_WIDTH // 2) * CELL_SIZE
        center_y = (GRID_HEIGHT // 2) * CELL_SIZE
        super().__init__(position=(center_x, center_y), body_color=GREEN)

        self.length: int = 1
        self.positions: List[Tuple[int, int]] = [self.position]
        self.direction: Tuple[int, int] = RIGHT
        self.next_direction: Optional[Tuple[int, int]] = None
        self._last_tail: Optional[Tuple[int, int]] = None

    def get_head_position(self) -> Tuple[int, int]:
        """
        Get current snake head position.
        """
        return self.positions[0]

    def update_direction(self) -> None:
        """
        Apply next_direction if it is set and not opposite to current direction.
        """
        if self.next_direction is None:
            return

        dx, dy = self.direction
        ndx, ndy = self.next_direction

        # Forbid instant reverse: RIGHT + LEFT = (0, 0)
        if (dx + ndx, dy + ndy) == (0, 0):
            self.next_direction = None
            return

        self.direction = self.next_direction
        self.next_direction = None

    def move(self) -> None:
        """
        Move snake by one cell.

        Inserts new head and removes tail if snake did not grow.
        Stores removed tail to erase it on draw.
        """
        head_x, head_y = self.get_head_position()
        dx, dy = self.direction

        new_head = wrap_position((head_x + dx, head_y + dy))
        self.positions.insert(0, new_head)

        self._last_tail = None
        if len(self.positions) > self.length:
            self._last_tail = self.positions.pop()

        self.position = new_head

    def reset(self) -> None:
        """
        Reset snake to initial state (after self-collision).
        """
        center_x = (GRID_WIDTH // 2) * CELL_SIZE
        center_y = (GRID_HEIGHT // 2) * CELL_SIZE

        self.length = 1
        self.positions = [(center_x, center_y)]
        self.direction = RIGHT
        self.next_direction = None
        self._last_tail = None
        self.position = self.positions[0]

    def draw(self, surface: pygame.Surface) -> None:
        """
        Draw the snake and erase the last tail cell to avoid leaving trail.
        """
        for x, y in self.positions:
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, self.body_color, rect)

        if self._last_tail is not None:
            tx, ty = self._last_tail
            rect = pygame.Rect(tx, ty, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, BLACK, rect)


def handle_keys(snake: Snake) -> None:
    """
    Process pygame events and update snake.next_direction.

    Args:
        snake: Snake instance to control.
    """
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            raise SystemExit

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                snake.next_direction = UP
            elif event.key == pygame.K_DOWN:
                snake.next_direction = DOWN
            elif event.key == pygame.K_LEFT:
                snake.next_direction = LEFT
            elif event.key == pygame.K_RIGHT:
                snake.next_direction = RIGHT


def main() -> None:
    """
    Main game loop:
    - handle input
    - update snake direction
    - move snake
    - check apple eating
    - check self-collision (reset)
    - draw objects and update display
    """
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Изгиб Питона")
    clock = pygame.time.Clock()

    screen.fill(BLACK)

    snake = Snake()
    apple = Apple()
    apple.randomize_position(forbidden=snake.positions)
    apple.draw(screen)
    snake.draw(screen)
    pygame.display.update()

    while True:
        clock.tick(FPS)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        # Eat apple
        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position(forbidden=snake.positions)

        # Self collision -> reset
        head = snake.get_head_position()
        if head in snake.positions[1:]:
            screen.fill(BLACK)
            snake.reset()
            apple.randomize_position(forbidden=snake.positions)

        snake.draw(screen)
        apple.draw(screen)
        pygame.display.update()


if __name__ == "__main__":
    main()
