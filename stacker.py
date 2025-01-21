import pygame
import sys

pygame.init()

# --------------------------
#  CONFIGURATION CONSTANTS
# --------------------------
NUM_COLS = 7
NUM_ROWS = 15
CELL_SIZE = 40
FPS = 30

SCOREBOARD_WIDTH = 200  # Right-hand side area
GAME_WIDTH = NUM_COLS * CELL_SIZE     # 7*40 = 280
GAME_HEIGHT = NUM_ROWS * CELL_SIZE    # 15*40 = 600

WINDOW_WIDTH = GAME_WIDTH + SCOREBOARD_WIDTH
WINDOW_HEIGHT = GAME_HEIGHT

# Colors
BACKGROUND_COLOR  = ( 0,  0, 0)   # main game area background
PANEL_COLOR       = ( 50,  50,  50)   # side panel background
BLOCK_COLOR       = (200,  50,  50)
BORDER_COLOR      = (0, 0, 0)
TEXT_COLOR        = (255, 255, 255)
HIGHLIGHT_COLOR   = (255, 200,   0)
FLASH_COLOR       = (255,  50,  50)

FLASH_DURATION    = 2.0  # seconds to flash the failed block

# Fonts
font       = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Create the window with double buffering to reduce flicker
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.DOUBLEBUF)
pygame.display.set_caption("Blockers")
clock = pygame.time.Clock()

# --------------------------
#   GLOBAL VARIABLES
# --------------------------
HIGH_SCORE = 0               # Highest score so far
LEADERBOARD = []             # List of (score, initials), up to 5
asked_for_initials = False   # Flag to avoid re-prompting for initials

# Try loading a logo
try:
    game_logo = pygame.image.load("stacker_logo.png")
except Exception as e:
    print("Warning: Could not load 'stacker_logo.png'.", e)
    game_logo = None


def draw_text(surface, text, x, y, color=TEXT_COLOR, font_obj=font, center=False):
    """
    Draw text on the surface. If center=True, (x, y) is the center of the text,
    else it's the top-left corner.
    """
    img = font_obj.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(img, rect)


def compute_overlap(row_below, row_current):
    """
    Computes how many columns the current row overlaps with the row below.
    """
    p_b, w_b = int(row_below.position), row_below.width
    p_c, w_c = int(row_current.position), row_current.width
    left  = max(p_b, p_c)
    right = min(p_b + w_b, p_c + w_c)
    return right - left


def update_row_for_overlap(current_row, row_below, overlap):
    """
    Adjust current_row so it only occupies the overlapping columns.
    """
    p_b = int(row_below.position)
    p_c = int(current_row.position)
    overlap_left = max(p_b, p_c)

    current_row.position = float(overlap_left)
    current_row.width = overlap


def get_speed_for_row(y_index):
    """
    Speed increases slightly each row up.
    """
    base_speed = 0.3
    speed_increment = 0.03
    return base_speed + (speed_increment * y_index)


class Row:
    """
    A row in the stacker game.
    """
    def __init__(self, width, position, y_index, direction=1, speed=0.0):
        self.width = width
        self.position = float(position)
        self.y_index = y_index
        self.direction = direction
        self.speed = speed

    def update(self):
        """ Move horizontally, sliding fully off-screen before reversing. """
        if self.direction != 0 and self.speed > 0:
            self.position += self.direction * self.speed
            # Round the float to reduce jitter/flicker
            self.position = round(self.position, 3)

            if self.direction > 0:  # moving right
                if self.position > NUM_COLS:
                    self.position = float(NUM_COLS)
                    self.direction = -1
            else:  # moving left
                if (self.position + self.width) < 0:
                    self.position = float(-self.width)
                    self.direction = +1

    def draw(self, surface, block_color=None):
        if block_color is None:
            block_color = BLOCK_COLOR

        left_col = int(self.position)
        for i in range(self.width):
            col_index = left_col + i
            pixel_x = col_index * CELL_SIZE
            pixel_y = (NUM_ROWS - 1 - self.y_index) * CELL_SIZE

            rect = pygame.Rect(pixel_x, pixel_y, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, block_color, rect)
            pygame.draw.rect(surface, BORDER_COLOR, rect, width=1)


def add_leaderboard_entry(score, initials):
    """
    Insert the new (score, initials) into LEADERBOARD, sorted desc by score.
    Keep only top 5.
    """
    global LEADERBOARD
    LEADERBOARD.append((score, initials))
    LEADERBOARD.sort(key=lambda x: x[0], reverse=True)
    LEADERBOARD = LEADERBOARD[:5]


def draw_leaderboard(surface):
    """
    Draw the top-5 high scores at the bottom portion of the side panel.
    """
    margin_left = GAME_WIDTH + 20
    margin_top = 300

    draw_text(surface, "High Scores:", margin_left, margin_top, color=HIGHLIGHT_COLOR, font_obj=small_font)
    margin_top += 25

    if not LEADERBOARD:
        draw_text(surface, "No records yet", margin_left, margin_top, font_obj=small_font)
        return

    for i, (sc, init) in enumerate(LEADERBOARD):
        line = f"{i+1}. {init} - {sc}"
        draw_text(surface, line, margin_left, margin_top, font_obj=small_font)
        margin_top += 20


def draw_side_panel():
    """
    Draw the side panel: background, logo/title, instructions, and leaderboard.
    """
    panel_rect = pygame.Rect(GAME_WIDTH, 0, SCOREBOARD_WIDTH, GAME_HEIGHT)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect)

    margin_left = GAME_WIDTH + 20
    margin_top = 20

    # Logo or text
    if game_logo:
        screen.blit(game_logo, (margin_left, margin_top))
        margin_top += game_logo.get_height() + 10
    else:
        draw_text(screen, "STACKER", margin_left, margin_top, color=HIGHLIGHT_COLOR)
        margin_top += 40

    # Instructions
    instructions = [
        "Press SPACE",
        "to lock row",
        "",
        "Press R",
        "to restart",
        "",
        "Press ESC",
        "to quit"
    ]
    for line in instructions:
        draw_text(screen, line, margin_left, margin_top, color=TEXT_COLOR, font_obj=small_font)
        margin_top += 25

    # Leaderboard
    draw_leaderboard(screen)


def prompt_for_initials():
    """
    Let the user type up to 3 letters for the new record.
    Returns the initials string (uppercased) or None if user quits.
    """
    initials = ""
    entering = True

    # We'll produce a minimal prompt for initials in the main area
    while entering:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_BACKSPACE:
                    initials = initials[:-1]
                elif event.key == pygame.K_RETURN:
                    entering = False
                else:
                    # only accept letters A-Z, up to 3
                    if len(initials) < 3:
                        if event.unicode.isalpha():
                            initials += event.unicode.upper()

        # Draw minimal UI
        screen.fill(BACKGROUND_COLOR, (0, 0, GAME_WIDTH, GAME_HEIGHT))
        screen.fill(PANEL_COLOR, (GAME_WIDTH, 0, SCOREBOARD_WIDTH, GAME_HEIGHT))

        draw_text(screen, "NEW HIGH SCORE!", GAME_WIDTH//2, GAME_HEIGHT//2 - 40, color=HIGHLIGHT_COLOR, center=True)
        draw_text(screen, f"Enter Initials: {initials}", GAME_WIDTH//2, GAME_HEIGHT//2, center=True)
        draw_text(screen, "(Press Enter when done)", GAME_WIDTH//2, GAME_HEIGHT//2 + 40, font_obj=small_font, center=True)

        pygame.display.flip()

    return initials


def run_game():
    global HIGH_SCORE, LEADERBOARD, asked_for_initials

    asked_for_initials = False  # reset for each new game

    # Bottom row
    bottom_row = Row(width=NUM_COLS, position=0, y_index=0, direction=0, speed=0)
    rows = [bottom_row]

    TARGET_ROW = NUM_ROWS - 1
    current_row_index = 1

    # First moving row
    initial_width = 3
    initial_pos = (NUM_COLS - initial_width) // 2
    initial_speed = get_speed_for_row(current_row_index)
    moving_row = Row(
        width=initial_width,
        position=initial_pos,
        y_index=current_row_index,
        direction=1,
        speed=initial_speed
    )

    game_over = False
    flash_failed = False
    fail_flash_timer = 0.0
    won = False
    failed_row = None
    score = 0

    while True:
        dt = clock.tick(FPS) / 1000.0

        # EVENT
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                # Lock the row if not flashing or over
                if not flash_failed and not game_over:
                    if event.key == pygame.K_SPACE:
                        overlap = compute_overlap(rows[-1], moving_row)
                        if overlap <= 0:
                            # Start flashing fail
                            flash_failed = True
                            fail_flash_timer = FLASH_DURATION
                            failed_row = Row(
                                width=moving_row.width,
                                position=moving_row.position,
                                y_index=moving_row.y_index,
                                direction=0,
                                speed=0
                            )
                        else:
                            # Lock success
                            score += 1
                            if score > HIGH_SCORE:
                                HIGH_SCORE = score
                            update_row_for_overlap(moving_row, rows[-1], overlap)
                            rows.append(moving_row)

                            if current_row_index == TARGET_ROW:
                                won = True
                                game_over = True
                            else:
                                current_row_index += 1
                                new_w = overlap
                                new_pos = int(moving_row.position)
                                new_spd = get_speed_for_row(current_row_index)
                                moving_row = Row(
                                    width=new_w,
                                    position=new_pos,
                                    y_index=current_row_index,
                                    direction=1,
                                    speed=new_spd
                                )

                # Press R to restart if game ended
                if game_over or (flash_failed and fail_flash_timer <= 0):
                    if event.key == pygame.K_r:
                        return True

        # UPDATE
        if not flash_failed and not game_over:
            moving_row.update()
        elif flash_failed:
            fail_flash_timer -= dt
            if fail_flash_timer <= 0:
                flash_failed = False
                game_over = True

        # DRAW
        # 1) Clear main game area
        screen.fill(BACKGROUND_COLOR, (0,0, GAME_WIDTH, GAME_HEIGHT))

        # 2) Draw locked rows
        for row in rows:
            row.draw(screen)

        # 3) Draw moving row if not flashing/over
        if not flash_failed and not game_over:
            moving_row.draw(screen)
        else:
            # If flashing
            if flash_failed and fail_flash_timer > 0:
                blink_rate = 0.2
                intervals = int((FLASH_DURATION - fail_flash_timer) / blink_rate)
                color = FLASH_COLOR if (intervals % 2 == 0) else BACKGROUND_COLOR
                if failed_row:
                    failed_row.draw(screen, block_color=color)

        # 4) Score in top-left
        draw_text(screen, f"Score: {score}", 10, 10)

        # 5) High score in top-right
        high_str = f"High: {HIGH_SCORE}"
        high_img = font.render(high_str, True, TEXT_COLOR)
        w = high_img.get_width()
        screen.blit(high_img, (GAME_WIDTH - w - 10, 10))

        # 6) If game is over & not flashing => display result
        if game_over and not flash_failed:
            if won:
                msg = "YOU WIN!"
            else:
                msg = "GAME OVER"
            cx = GAME_WIDTH // 2
            cy = GAME_HEIGHT // 2
            draw_text(screen, msg, cx, cy, color=HIGHLIGHT_COLOR, center=True)

            draw_text(screen, "Press R to Restart", cx, cy+40, center=True)
            draw_text(screen, "Press ESC to Quit", cx, cy+80, center=True)

            # Prompt for initials if new all-time best, only once
            if (score == HIGH_SCORE and score > 0 and not asked_for_initials):
                # check if scoreboard is empty or this is >= the best
                best_score = LEADERBOARD[0][0] if LEADERBOARD else 0
                if score >= best_score:
                    asked_for_initials = True  # so we don't ask again
                    user_init = prompt_for_initials()
                    if user_init:
                        add_leaderboard_entry(score, user_init)

        # 7) Draw side panel
        draw_side_panel()

        pygame.display.flip()


def main():
    while True:
        do_restart = run_game()
        if not do_restart:
            break
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
