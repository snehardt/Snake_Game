"""Start Snake and handle player input, the game loop, and music."""

from pathlib import Path
import pygame

from game import MAP_SIZES, MOVEMENT_SPEEDS, SnakeGame
from drawing import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SIZE, draw_board, draw_button,
    draw_game_over, draw_scoreboard, draw_settings, draw_snake_and_fruit,
    settings_buttons,
)


MUSIC_DIRECTORY = Path(__file__).resolve().parent / "music"


MUSIC_VOLUME = 0.35


FRAMES_PER_SECOND = 60


def start_background_music():
    """Loop an optional music file, allowing play when audio is unavailable."""
    if pygame.mixer.get_init() is None:
        return False
    for extension in ("ogg", "mp3", "wav"):
        music_file = MUSIC_DIRECTORY / f"background.{extension}"
        if not music_file.is_file():
            continue
        try:
            pygame.mixer.music.load(str(music_file))
            pygame.mixer.music.set_volume(MUSIC_VOLUME)
            pygame.mixer.music.play(-1)
            return True
        except pygame.error as error:
            print(f"Could not play {music_file.name}: {error}")
    return False


def main():
    """Read input, update the current round, and draw the game or its menus."""
    pygame.init()
    music_playing = start_background_music()
    music_muted = False
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Snake")
    clock = pygame.time.Clock()
    button_font = pygame.font.Font(None, 40)
    scoreboard_font = pygame.font.Font(None, 32)

    start_button = pygame.Rect(0, 0, 240, 64)
    start_button.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 42)
    settings_button = pygame.Rect(0, 0, 240, 64)
    settings_button.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 42)
    buttons = settings_buttons()
    size_buttons, speed_buttons, done_button = buttons
    map_size = "Normal"
    speed = "Normal"
    settings_open = False
    game = None

    key_directions = {
        pygame.K_UP: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_LEFT: (-1, 0),
        pygame.K_RIGHT: (1, 0),
    }

    running = True
    while running:
        elapsed_ms = clock.tick(FRAMES_PER_SECOND)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m and music_playing:
                    music_muted = not music_muted
                    pygame.mixer.music.set_volume(0 if music_muted else MUSIC_VOLUME)
                elif event.key == pygame.K_ESCAPE:
                    if settings_open:
                        settings_open = False
                    else:
                        running = False
                elif not settings_open and game is not None and event.key in key_directions:
                    game.turn(key_directions[event.key])
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if settings_open:
                    for name, rectangle in size_buttons.items():
                        if rectangle.collidepoint(event.pos):
                            map_size = name
                    for name, rectangle in speed_buttons.items():
                        if rectangle.collidepoint(event.pos):
                            speed = name
                    if done_button.collidepoint(event.pos):
                        settings_open = False
                elif game is None or game.game_over:
                    if start_button.collidepoint(event.pos):
                        columns = MAP_SIZES[map_size]
                        game = SnakeGame(columns, columns, MOVEMENT_SPEEDS[speed])
                        elapsed_ms = 0  # Ignore time from before this round.
                    elif settings_button.collidepoint(event.pos):
                        settings_open = True

        if not running:
            break

        if game is not None and not settings_open:
            game.update(elapsed_ms)

        if game is not None and not settings_open:
            draw_board(screen, game.columns, game.rows)
            draw_snake_and_fruit(screen, game)
            if game.game_over:
                draw_game_over(screen, game, start_button, settings_button, button_font)
        else:
            columns = MAP_SIZES[map_size]
            draw_board(screen, columns, columns)
            if settings_open:
                draw_settings(screen, map_size, speed, buttons, button_font, scoreboard_font)
            else:
                draw_button(screen, start_button, "Start", button_font)
                draw_button(screen, settings_button, "Settings", button_font)
        draw_scoreboard(screen, game, scoreboard_font)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
