#!/usr/bin/env python3
"""
Key Door Puzzle - Match keys to doors by shape.

Controls:
    Arrow keys or WASD to move the key
    Mouse to move the key (alternative)
    ESC to quit
    SPACE or ENTER to start next level / restart

Author: Orami
"""

import pygame
import random
import sys
import math

# ============================================================
# CONSTANTS
# ============================================================

# Window
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Key Door Puzzle"
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (40, 40, 40)

# Shape colors
COLORS = {
    "square": (50, 150, 255),      # Blue
    "triangle": (50, 200, 100),    # Green
    "circle": (220, 80, 80),       # Red
    "star": (255, 200, 50),        # Yellow
}

SHAPES = list(COLORS.keys())

# Game settings
KEY_SIZE = 30
DOOR_WIDTH = 60
DOOR_HEIGHT = 90
KEY_SPEED = 5
INITIAL_TIME = 30
TIME_REDUCTION = 2
MIN_TIME = 10
INITIAL_LIVES = 3
DOOR_MARGIN = 40


# ============================================================
# DRAWING FUNCTIONS
# ============================================================

def draw_square(surface, x, y, size, color, filled=True):
    """Draw a square shape."""
    rect = pygame.Rect(x - size // 2, y - size // 2, size, size)
    if filled:
        pygame.draw.rect(surface, color, rect)
    pygame.draw.rect(surface, WHITE, rect, 2)


def draw_triangle(surface, x, y, size, color, filled=True):
    """Draw a triangle shape."""
    points = [
        (x, y - size // 2),
        (x - size // 2, y + size // 2),
        (x + size // 2, y + size // 2),
    ]
    if filled:
        pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, WHITE, points, 2)


def draw_circle(surface, x, y, size, color, filled=True):
    """Draw a circle shape."""
    radius = size // 2
    if filled:
        pygame.draw.circle(surface, color, (x, y), radius)
    pygame.draw.circle(surface, WHITE, (x, y), radius, 2)


def draw_star(surface, x, y, size, color, filled=True):
    """Draw a 5-pointed star shape."""
    points = []
    for i in range(10):
        angle = math.radians(i * 36 - 90)
        radius = size // 2 if i % 2 == 0 else size // 4
        px = x + radius * math.cos(angle)
        py = y + radius * math.sin(angle)
        points.append((px, py))

    if filled:
        pygame.draw.polygon(surface, color, points)
    pygame.draw.polygon(surface, WHITE, points, 2)


def draw_shape(surface, shape, x, y, size, color, filled=True):
    """Draw any shape by name."""
    if shape == "square":
        draw_square(surface, x, y, size, color, filled)
    elif shape == "triangle":
        draw_triangle(surface, x, y, size, color, filled)
    elif shape == "circle":
        draw_circle(surface, x, y, size, color, filled)
    elif shape == "star":
        draw_star(surface, x, y, size, color, filled)


def get_shape_rect(shape, x, y, size):
    """Get collision rectangle for a shape."""
    return pygame.Rect(x - size // 2, y - size // 2, size, size)


# ============================================================
# KEY CLASS
# ============================================================

class Key:
    """Key that the player moves to match a door."""

    def __init__(self, shape, x, y):
        self.shape = shape
        self.color = COLORS[shape]
        self.x = x
        self.y = y
        self.size = KEY_SIZE
        self.speed = KEY_SPEED
        self.target_door = None
        self.inserted = False

    def update(self, keys_pressed, mouse_pos=None):
        """Move key based on input."""
        if mouse_pos:
            # Smooth movement toward mouse
            dx = mouse_pos[0] - self.x
            dy = mouse_pos[1] - self.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 5:
                self.x += (dx / dist) * self.speed * 2
                self.y += (dy / dist) * self.speed * 2
        else:
            # Arrow/WASD movement
            if keys_pressed[pygame.K_LEFT] or keys_pressed[pygame.K_a]:
                self.x -= self.speed
            if keys_pressed[pygame.K_RIGHT] or keys_pressed[pygame.K_d]:
                self.x += self.speed
            if keys_pressed[pygame.K_UP] or keys_pressed[pygame.K_w]:
                self.y -= self.speed
            if keys_pressed[pygame.K_DOWN] or keys_pressed[pygame.K_s]:
                self.y += self.speed

        # Keep within bounds
        self.x = max(self.size, min(WINDOW_WIDTH - self.size, self.x))
        self.y = max(self.size, min(WINDOW_HEIGHT - self.size, self.y))

    def get_rect(self):
        """Get collision rectangle."""
        return get_shape_rect(self.shape, self.x, self.y, self.size)

    def draw(self, surface):
        """Draw the key."""
        draw_shape(surface, self.shape, self.x, self.y, self.size, self.color)

        # Draw key handle (small circle at bottom)
        handle_y = self.y + self.size // 2 + 10
        pygame.draw.circle(surface, self.color, (int(self.x), int(handle_y)), 8)
        pygame.draw.circle(surface, WHITE, (int(self.x), int(handle_y)), 8, 2)


# ============================================================
# DOOR CLASS
# ============================================================

class Door:
    """Door that accepts a key of matching shape."""

    def __init__(self, shape, x, y):
        self.shape = shape
        self.color = COLORS[shape]
        self.x = x
        self.y = y
        self.width = DOOR_WIDTH
        self.height = DOOR_HEIGHT
        self.opened = False
        self.flash_timer = 0

    def check_collision(self, key):
        """Check if key matches this door."""
        if key.shape != self.shape:
            return False

        door_rect = self.get_rect()
        key_rect = key.get_rect()
        return door_rect.colliderect(key_rect)

    def open(self):
        """Mark door as opened."""
        self.opened = True
        self.flash_timer = 30

    def update(self):
        """Update door animation."""
        if self.flash_timer > 0:
            self.flash_timer -= 1

    def get_rect(self):
        """Get collision rectangle."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )

    def draw(self, surface):
        """Draw the door."""
        rect = self.get_rect()

        if self.opened:
            # Open door - darker interior
            pygame.draw.rect(surface, DARK_GRAY, rect)
            pygame.draw.rect(surface, self.color, rect, 3)

            # Draw checkmark
            check_color = GREEN if self.flash_timer > 0 else self.color
            pygame.draw.line(surface, check_color,
                           (self.x - 15, self.y),
                           (self.x - 5, self.y + 10), 3)
            pygame.draw.line(surface, check_color,
                           (self.x - 5, self.y + 10),
                           (self.x + 15, self.y - 10), 3)
        else:
            # Closed door
            pygame.draw.rect(surface, GRAY, rect)
            pygame.draw.rect(surface, self.color, rect, 3)

            # Draw keyhole shape
            draw_shape(surface, self.shape, self.x, self.y, 25, self.color, False)

            # Draw handle
            handle_x = self.x + self.width // 2 - 10
            pygame.draw.circle(surface, self.color, (handle_x, self.y), 5)


# ============================================================
# LEVEL CLASS
# ============================================================

class Level:
    """A single game level with doors and a key."""

    def __init__(self, level_number):
        self.level_number = level_number
        self.doors = []
        self.key = None
        self.completed = False
        self.time_limit = max(MIN_TIME, INITIAL_TIME - level_number * TIME_REDUCTION)
        self.timer = self.time_limit
        self.setup_level()

    def setup_level(self):
        """Create doors and key for this level."""
        # Number of doors increases with level
        num_doors = min(4, 2 + self.level_number // 2)

        # Randomly select shapes for doors
        door_shapes = random.sample(SHAPES, num_doors)

        # Calculate door positions (spread across the top)
        total_width = num_doors * (DOOR_WIDTH + DOOR_MARGIN) - DOOR_MARGIN
        start_x = (WINDOW_WIDTH - total_width) // 2 + DOOR_WIDTH // 2

        for i, shape in enumerate(door_shapes):
            x = start_x + i * (DOOR_WIDTH + DOOR_MARGIN)
            y = 100
            self.doors.append(Door(shape, x, y))

        # Create key (must match one of the doors)
        key_shape = random.choice(door_shapes)
        key_x = WINDOW_WIDTH // 2
        key_y = WINDOW_HEIGHT - 100
        self.key = Key(key_shape, key_x, key_y)

    def update(self):
        """Update level state."""
        self.timer -= 1 / FPS

        for door in self.doors:
            door.update()

        # Check if key reached correct door
        for door in self.doors:
            if not door.opened and door.check_collision(self.key):
                door.open()
                self.key.inserted = True
                self.completed = True
                return True

        # Check time out
        if self.timer <= 0:
            return False

        return None

    def draw(self, surface):
        """Draw the level."""
        # Draw doors
        for door in self.doors:
            door.draw(surface)

        # Draw key
        if not self.key.inserted:
            self.key.draw(surface)


# ============================================================
# GAME CLASS
# ============================================================

class Game:
    """Main game controller."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(WINDOW_TITLE)
        self.clock = pygame.time.Clock()

        # Fonts (using Font instead of SysFont for Python 3.14 compatibility)
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 28)
        self.font_small = pygame.font.Font(None, 20)
        self.font_tiny = pygame.font.Font(None, 16)

        self.state = "menu"  # menu, playing, level_complete, game_over, win
        self.level_number = 0
        self.lives = INITIAL_LIVES
        self.score = 0
        self.high_score = 0
        self.level = None
        self.running = True
        self.use_mouse = True

    def start_game(self):
        """Start a new game."""
        self.level_number = 1
        self.lives = INITIAL_LIVES
        self.score = 0
        self.level = Level(self.level_number)
        self.state = "playing"

    def next_level(self):
        """Advance to the next level."""
        self.level_number += 1
        self.score += 100
        self.level = Level(self.level_number)
        self.state = "playing"

    def handle_events(self):
        """Process all input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == "playing":
                        self.state = "menu"
                    else:
                        self.running = False
                    return

                if event.key == pygame.K_TAB:
                    self.use_mouse = not self.use_mouse

                if self.state == "menu":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.start_game()

                elif self.state == "playing":
                    pass  # Handled in update

                elif self.state == "level_complete":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.next_level()

                elif self.state == "game_over":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.state = "menu"

                elif self.state == "win":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        self.state = "menu"

    def update(self):
        """Update game state."""
        if self.state != "playing":
            return

        # Update key movement
        keys_pressed = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos() if self.use_mouse else None
        self.level.key.update(keys_pressed, mouse_pos)

        # Update level
        result = self.level.update()

        if result is True:
            # Level completed
            self.score += int(self.level.timer) * 10
            if self.level_number >= 10:
                self.state = "win"
                if self.score > self.high_score:
                    self.high_score = self.score
            else:
                self.state = "level_complete"

        elif result is False:
            # Time out - lose a life
            self.lives -= 1
            if self.lives <= 0:
                self.state = "game_over"
                if self.score > self.high_score:
                    self.high_score = self.score
            else:
                # Restart current level
                self.level = Level(self.level_number)

    def draw_menu(self):
        """Draw main menu."""
        self.screen.fill(BLACK)

        # Title
        title = self.font_large.render("KEY DOOR PUZZLE", True, WHITE)
        title_rect = title.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)

        # Draw sample shapes
        for i, shape in enumerate(SHAPES):
            x = WINDOW_WIDTH // 2 - 150 + i * 100
            y = 250
            draw_shape(self.screen, shape, x, y, 40, COLORS[shape])

        # Instructions
        instructions = [
            "Match the key to the correct door",
            "",
            "Arrow keys / WASD / Mouse to move",
            "TAB to switch control mode",
            "",
            "Press SPACE to start",
        ]
        for i, line in enumerate(instructions):
            color = WHITE if line else WHITE
            text = self.font_small.render(line, True, GRAY if not line else WHITE)
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, 350 + i * 30))
            self.screen.blit(text, text_rect)

    def draw_hud(self):
        """Draw heads-up display."""
        # Level
        level_text = self.font_small.render(
            f"Level: {self.level_number}/10", True, WHITE
        )
        self.screen.blit(level_text, (10, 10))

        # Lives
        lives_text = self.font_small.render(
            f"Lives: {self.lives}", True, (220, 50, 50)
        )
        self.screen.blit(lives_text, (10, 35))

        # Score
        score_text = self.font_small.render(
            f"Score: {self.score}", True, (255, 200, 50)
        )
        self.screen.blit(score_text, (WINDOW_WIDTH - score_text.get_width() - 10, 10))

        # Timer
        time_color = WHITE
        if self.level.timer < 10:
            time_color = (220, 50, 50)
        timer_text = self.font_small.render(
            f"Time: {int(self.level.timer)}s", True, time_color
        )
        self.screen.blit(timer_text, (WINDOW_WIDTH - timer_text.get_width() - 10, 35))

        # Control mode
        mode = "Mouse" if self.use_mouse else "Keyboard"
        mode_text = self.font_tiny.render(
            f"Controls: {mode} (TAB to switch)", True, GRAY
        )
        self.screen.blit(mode_text, (10, WINDOW_HEIGHT - 25))

        # Key shape hint
        hint = f"Find the {self.level.key.shape} door"
        hint_text = self.font_small.render(hint, True, self.level.key.color)
        hint_rect = hint_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 25))
        self.screen.blit(hint_text, hint_rect)

    def draw_level_complete(self):
        """Draw level complete screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        text = self.font_large.render("LEVEL COMPLETE!", True, (50, 200, 50))
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30))
        self.screen.blit(text, rect)

        bonus = f"Time bonus: +{int(self.level.timer) * 10} points"
        bonus_text = self.font_medium.render(bonus, True, WHITE)
        bonus_rect = bonus_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20))
        self.screen.blit(bonus_text, bonus_rect)

        next_text = self.font_small.render(
            "Press SPACE for next level", True, GRAY
        )
        next_rect = next_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 70))
        self.screen.blit(next_text, next_rect)

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        text = self.font_large.render("GAME OVER", True, (220, 50, 50))
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(text, rect)

        score_text = self.font_medium.render(
            f"Final Score: {self.score}", True, WHITE
        )
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)

        restart_text = self.font_small.render(
            "Press SPACE to return to menu", True, GRAY
        )
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def draw_win(self):
        """Draw win screen."""
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        text = self.font_large.render("YOU WIN!", True, (255, 200, 50))
        rect = text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 40))
        self.screen.blit(text, rect)

        score_text = self.font_medium.render(
            f"Final Score: {self.score}", True, WHITE
        )
        score_rect = score_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 10))
        self.screen.blit(score_text, score_rect)

        restart_text = self.font_small.render(
            "Press SPACE to return to menu", True, GRAY
        )
        restart_rect = restart_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()

            # Draw based on state
            if self.state == "menu":
                self.draw_menu()
            elif self.state == "playing":
                self.screen.fill(BLACK)
                self.level.draw(self.screen)
                self.draw_hud()
            elif self.state == "level_complete":
                self.screen.fill(BLACK)
                self.level.draw(self.screen)
                self.draw_hud()
                self.draw_level_complete()
            elif self.state == "game_over":
                self.draw_game_over()
            elif self.state == "win":
                self.draw_win()

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    game = Game()
    game.run()
