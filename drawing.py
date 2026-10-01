"""Draw the board, snake, apple, scoreboard, and menus."""

import pygame

from game import BOARD_COLUMNS, BOARD_ROWS, MAP_SIZES, MOVEMENT_SPEEDS


CELL_SIZE = 35


SCOREBOARD_HEIGHT = 72


WINDOW_WIDTH = BOARD_COLUMNS * CELL_SIZE


WINDOW_HEIGHT = BOARD_ROWS * CELL_SIZE + SCOREBOARD_HEIGHT


WINDOW_SIZE = (WINDOW_WIDTH, WINDOW_HEIGHT)


LIGHT_GREEN = (170, 215, 81)


DARK_GREEN = (162, 209, 73)


PLAYER_COLOR = (35, 85, 190)


HEAD_COLOR = (12, 24, 65)


TAIL_COLOR = (100, 185, 245)


BLACK = (0, 0, 0)


STEM_COLOR = (100, 60, 25)


FRUIT_COLOR = (210, 45, 50)


WHITE = (255, 255, 255)


SCOREBOARD_COLOR = (18, 43, 60)


BUTTON_HOVER_COLOR = (45, 105, 210)


def format_time(milliseconds):
    """Convert a time such as 61,000 milliseconds to the text '01:01'."""
    total_seconds = milliseconds // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def draw_scoreboard(screen, game, font):
    """Draw the score and timer above the board."""
    pygame.draw.rect(screen, SCOREBOARD_COLOR, (0, 0, WINDOW_WIDTH, SCOREBOARD_HEIGHT))
    fruit_count = 0
    time_alive_ms = 0
    if game is not None:
        fruit_count = game.score
        time_alive_ms = game.alive_ms

    fruit_text = font.render(f"Fruit eaten: {fruit_count}", True, WHITE)
    time_text = font.render(f"Time alive: {format_time(time_alive_ms)}", True, WHITE)
    fruit_position = fruit_text.get_rect(midleft=(24, SCOREBOARD_HEIGHT // 2))
    time_position = time_text.get_rect(midright=(WINDOW_WIDTH - 24, SCOREBOARD_HEIGHT // 2))
    screen.blit(fruit_text, fruit_position)
    screen.blit(time_text, time_position)


def draw_button(screen, button_rectangle, label, font, selected=False):
    """Highlight hovered buttons and the currently selected setting."""
    button_color = PLAYER_COLOR
    if selected or button_rectangle.collidepoint(pygame.mouse.get_pos()):
        button_color = BUTTON_HOVER_COLOR
    pygame.draw.rect(screen, button_color, button_rectangle, border_radius=10)
    if selected:
        pygame.draw.rect(screen, WHITE, button_rectangle, width=3, border_radius=10)
    button_text = font.render(label, True, WHITE)
    screen.blit(button_text, button_text.get_rect(center=button_rectangle.center))


def board_layout(columns, rows):
    """Fit and center the map inside the fixed-size window."""
    cell_size = min(WINDOW_WIDTH // columns, (WINDOW_HEIGHT - SCOREBOARD_HEIGHT) // rows)
    left = (WINDOW_WIDTH - columns * cell_size) // 2
    top = SCOREBOARD_HEIGHT + (WINDOW_HEIGHT - SCOREBOARD_HEIGHT - rows * cell_size) // 2
    return cell_size, left, top


def draw_board(screen, columns=BOARD_COLUMNS, rows=BOARD_ROWS):
    """Draw a checkerboard for the selected map size."""
    screen.fill(SCOREBOARD_COLOR)
    cell_size, left, top = board_layout(columns, rows)
    for row in range(rows):
        for column in range(columns):
            square_color = LIGHT_GREEN if (row + column) % 2 == 0 else DARK_GREEN
            square_rectangle = (
                left + column * cell_size, top + row * cell_size, cell_size, cell_size
            )
            pygame.draw.rect(screen, square_color, square_rectangle)


def snake_color(segment_index, segment_count):
    """Fade from a dark head to a light blue tail."""
    progress = segment_index / max(1, segment_count - 1)
    return tuple(round(dark + (light - dark) * progress)
                 for dark, light in zip(HEAD_COLOR, TAIL_COLOR))


def draw_eyes(screen, head_rectangle, direction):
    """Place two cartoon eyes near the face, looking forward."""
    dx, dy = direction
    side_x, side_y = -dy, dx
    size = head_rectangle.width
    center_x, center_y = head_rectangle.center
    eye_radius = max(2, round(size * 0.14))
    pupil_radius = max(1, round(eye_radius * 0.5))
    for side in (-1, 1):
        eye_x = round(center_x + dx * size * 0.20 + side_x * side * size * 0.24)
        eye_y = round(center_y + dy * size * 0.20 + side_y * side * size * 0.24)
        pygame.draw.circle(screen, BLACK, (eye_x, eye_y), eye_radius + 1)
        pygame.draw.circle(screen, WHITE, (eye_x, eye_y), eye_radius)
        pupil_offset = max(1, eye_radius - pupil_radius - 1)
        pupil = (eye_x + dx * pupil_offset, eye_y + dy * pupil_offset)
        pygame.draw.circle(screen, BLACK, pupil, pupil_radius)


def draw_snake_and_fruit(screen, game):
    """Draw fruit and animated snake segments on this round's map."""
    cell_size, left, top = board_layout(game.columns, game.rows)
    if game.fruit is not None:
        column, row = game.fruit
        center_x = left + column * cell_size + cell_size // 2
        center_y = top + row * cell_size + cell_size // 2
        fruit_radius = max(2, cell_size // 2 - 4)
        pygame.draw.circle(screen, FRUIT_COLOR, (center_x, center_y), fruit_radius)
        stem_bottom = (center_x, center_y - fruit_radius + 2)
        stem_top = (center_x + max(1, cell_size // 12), top + row * cell_size + 1)
        pygame.draw.line(screen, STEM_COLOR, stem_bottom, stem_top,
                         width=max(1, cell_size // 12))

    path = game.render_path()
    pieces = []
    # Connect along each grid edge to fill bends without diagonal shortcuts.
    for index in reversed(range(len(path) - 1)):
        start, end = path[index:index + 2]
        start_x, start_y = (round(value * cell_size) for value in start)
        end_x, end_y = (round(value * cell_size) for value in end)
        rectangle = pygame.Rect(
            left + min(start_x, end_x), top + min(start_y, end_y),
            abs(end_x - start_x) + cell_size, abs(end_y - start_y) + cell_size,
        )
        color = snake_color(min(index, len(game.snake) - 1), len(game.snake))
        pieces.append((rectangle, color))

    positions = game.render_positions()
    # Draw toward the head so its face remains visible at bends.
    for index in reversed(range(len(positions))):
        column, row = positions[index]
        rectangle = pygame.Rect(left + round(column * cell_size),
                                top + round(row * cell_size), cell_size, cell_size)
        pieces.append((rectangle, snake_color(index, len(positions))))
        if index == 0:
            head_rectangle = rectangle

    bounds = pieces[0][0].unionall([rectangle for rectangle, color in pieces])
    snake_surface = pygame.Surface(bounds.size, pygame.SRCALPHA)
    for rectangle, color in pieces:
        pygame.draw.rect(snake_surface, color, rectangle.move(-bounds.x, -bounds.y))

    # Only pixels exposed to the background receive an outline.
    outline = pygame.mask.from_surface(snake_surface)
    interior = outline.copy()
    for offset in ((-1, 0), (1, 0), (0, -1), (0, 1)):
        interior = interior.overlap_mask(outline, offset)
    outline.erase(interior, (0, 0))
    outline.to_surface(snake_surface, setcolor=BLACK, unsetcolor=None)
    draw_eyes(snake_surface, head_rectangle.move(-bounds.x, -bounds.y), game.direction)
    screen.blit(snake_surface, bounds)


def draw_overlay(screen):
    """Darken the board behind menus while leaving the scoreboard visible."""
    dark_overlay = pygame.Surface(
        (WINDOW_WIDTH, WINDOW_HEIGHT - SCOREBOARD_HEIGHT), pygame.SRCALPHA
    )
    dark_overlay.fill((0, 0, 0, 170))
    screen.blit(dark_overlay, (0, SCOREBOARD_HEIGHT))


def draw_game_over(screen, game, start_button, settings_button, font):
    """Show the result with options to restart or adjust settings."""
    draw_overlay(screen)
    title = "You Win!" if game.won else "Game Over"
    title_text = font.render(title, True, WHITE)
    score_text = font.render(f"Fruit eaten: {game.score}", True, WHITE)
    screen.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH // 2, 210)))
    screen.blit(score_text, score_text.get_rect(center=(WINDOW_WIDTH // 2, 250)))
    draw_button(screen, start_button, "Play Again", font)
    draw_button(screen, settings_button, "Settings", font)


def settings_buttons():
    """Arrange the map choices, speed choices, and return button."""
    size_buttons = {
        name: pygame.Rect(30 + index * 130, 290, 120, 56)
        for index, name in enumerate(MAP_SIZES)
    }
    speed_buttons = {
        name: pygame.Rect(100 + index * 170, 440, 160, 56)
        for index, name in enumerate(MOVEMENT_SPEEDS)
    }
    done_button = pygame.Rect(WINDOW_WIDTH // 2 - 120, 570, 240, 64)
    return size_buttons, speed_buttons, done_button


def draw_settings(screen, map_size, speed, buttons, font, detail_font):
    """Show independent map and speed choices for the next round."""
    draw_overlay(screen)
    size_buttons, speed_buttons, done_button = buttons
    columns = MAP_SIZES[map_size]
    labels = [
        ("Settings", 160, font),
        (f"Map size: {map_size} ({columns} x {columns})", 245, detail_font),
        (f"Movement speed: {speed} ({MOVEMENT_SPEEDS[speed]} ms per square)", 395, detail_font),
        ("Changes apply when you start your next round.", 535, detail_font),
    ]
    for label, y, label_font in labels:
        text = label_font.render(label, True, WHITE)
        screen.blit(text, text.get_rect(center=(WINDOW_WIDTH // 2, y)))
    for name, rectangle in size_buttons.items():
        draw_button(screen, rectangle, name, detail_font, selected=name == map_size)
    for name, rectangle in speed_buttons.items():
        draw_button(screen, rectangle, name, detail_font, selected=name == speed)
    draw_button(screen, done_button, "Done", font)
