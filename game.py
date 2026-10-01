"""Snake rules, movement timing, and map presets."""

import random


BOARD_COLUMNS = 20


BOARD_ROWS = 20


MOVE_INTERVAL_MS = 200


MAP_SIZES = {
    "Tiny": 10,
    "Small": 15,
    "Normal": 20,
    "Big": 30,
    "Massive": 40,
}


MOVEMENT_SPEEDS = {"Fast": 100, "Normal": MOVE_INTERVAL_MS, "Slow": 300}


STARTING_LENGTHS = {10: 3, 15: 4, 20: 5, 30: 7, 40: 10}


class SnakeGame:
    """Track movement, fruit, collisions, and survival time for one round."""

    def __init__(self, columns=None, rows=None, move_interval_ms=None):
        self.columns = BOARD_COLUMNS if columns is None else columns
        self.rows = BOARD_ROWS if rows is None else rows
        self.move_interval_ms = (
            MOVE_INTERVAL_MS if move_interval_ms is None else move_interval_ms
        )
        center_column = self.columns // 2
        center_row = self.rows // 2

        # The head comes first and the tail comes last.
        starting_length = min(STARTING_LENGTHS.get(self.columns, 3), center_column + 1)
        self.snake = [
            (center_column - index, center_row)
            for index in range(starting_length)
        ]
        self.previous_snake = self.snake.copy()
        self.movement_elapsed = 0
        self.alive_ms = 0

        # Screen rows increase DOWNWARD, so up is (0, -1).
        self.direction = (1, 0)
        self.pending_direction = self.direction
        self.turned = False
        self.late_turn_available = False
        self.game_over = False
        self.won = False
        self.score = 0
        self.fruit = self.spawn_fruit()

    def spawn_fruit(self):
        """Choose an empty square, or return None if the board is full."""
        empty_squares = []
        for row in range(self.rows):
            for column in range(self.columns):
                square = (column, row)
                if square not in self.snake:
                    empty_squares.append(square)

        if len(empty_squares) == 0:
            return None
        return random.choice(empty_squares)

    def turn(self, new_direction):
        """Turn at the nearest square, accepting early and late input."""
        if self.game_over or self.turned:
            return

        column_change, row_change = self.direction
        opposite_direction = (-column_change, -row_change)
        if new_direction == self.direction or new_direction == opposite_direction:
            return  # Do not reverse straight into our own body.

        self.pending_direction = new_direction
        if self.late_turn_available and self.movement_elapsed < self.move_interval_ms / 2:
            # Before halfway, the departing square is still the closest one.
            self.snake = self.previous_snake.copy()
            self.step()
            return
        # Only one turn per move prevents two rapid presses from reversing us.
        self.turned = True

    def step(self):
        """Move one square, checking for collisions and fruit."""
        if self.game_over:
            return

        self.previous_snake = self.snake.copy()
        previous_direction = self.direction
        self.direction = self.pending_direction
        self.turned = False
        self.late_turn_available = False
        head_column, head_row = self.snake[0]
        column_change, row_change = self.direction
        next_column = head_column + column_change
        next_row = head_row + row_change
        new_head = (next_column, next_row)
        eating_fruit = new_head == self.fruit

        if eating_fruit:
            body_to_check = self.snake
        else:
            # We may enter the tail's square because it moves away this step.
            body_to_check = self.snake[:-1]

        outside_columns = next_column < 0 or next_column >= self.columns
        outside_rows = next_row < 0 or next_row >= self.rows
        hit_body = new_head in body_to_check
        if outside_columns or outside_rows or hit_body:
            self.game_over = True
            return

        self.snake.insert(0, new_head)
        if eating_fruit:
            self.score += 1
            self.fruit = self.spawn_fruit()
            if self.fruit is None:
                self.won = True
                self.game_over = True
        else:
            self.snake.pop()
            # Eating and existing turns cannot be undone by a late input.
            self.late_turn_available = self.direction == previous_direction
        # Eating keeps the old tail, making the snake one square longer.

    def update(self, elapsed_ms):
        """Use time since the previous frame to decide when to move."""
        if self.game_over:
            # Finish the last slide without increasing the survival timer.
            self.movement_elapsed = min(
                self.move_interval_ms, self.movement_elapsed + elapsed_ms
            )
            return

        remaining_ms = elapsed_ms
        # A slow frame may contain enough time for several moves. Process
        # each move so we still check every square for collisions.
        while remaining_ms > 0 and not self.game_over:
            time_until_move = self.move_interval_ms - self.movement_elapsed
            time_to_use = min(remaining_ms, time_until_move)
            self.movement_elapsed += time_to_use
            self.alive_ms += time_to_use
            remaining_ms -= time_to_use

            if self.movement_elapsed >= self.move_interval_ms:
                self.movement_elapsed = 0
                self.step()
        # Stopping at a collision also stops the timer at that moment.

    def render_positions(self):
        """Get smooth drawing positions without changing the game grid."""
        progress = min(1, self.movement_elapsed / self.move_interval_ms)
        drawing_positions = []
        for segment_index in range(len(self.snake)):
            column, row = self.snake[segment_index]
            # A new segment has no previous entry, so use the old tail.
            previous_index = min(segment_index, len(self.previous_snake) - 1)
            old_column, old_row = self.previous_snake[previous_index]

            drawing_column = old_column + (column - old_column) * progress
            drawing_row = old_row + (row - old_row) * progress
            drawing_positions.append((drawing_column, drawing_row))
        return drawing_positions

    def render_path(self):
        """Keep bends on grid squares while the head and tail slide."""
        positions = self.render_positions()
        return [positions[0]] + self.previous_snake[:len(self.snake) - 1] + [positions[-1]]
