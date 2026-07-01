import random
import tkinter as tk
import colorsys
import math

root = tk.Tk()
root.resizable(False, False)
root.title("Snake")

ROWS = 25
COL = 25
TILE_SIZE = 25

WINDOW_WIDTH = COL * TILE_SIZE
WINDOW_HEIGHT = ROWS * TILE_SIZE


class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y


canvas = tk.Canvas(
    root,
    width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT,
    bg="black",
    highlightthickness=0,
)
canvas.pack()

root.update()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_x = (screen_width - WINDOW_WIDTH) // 2
window_y = (screen_height - WINDOW_HEIGHT) // 2

root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{window_x}+{window_y}")


snake_head = Tile(5 * TILE_SIZE, 5 * TILE_SIZE)
snake_body = []
food = Tile(10 * TILE_SIZE, 10 * TILE_SIZE)

velocity_x = 0
velocity_y = 0
score = 0
game_over = False


def spawn_food():
    while True:
        x = random.randint(0, COL - 1) * TILE_SIZE
        y = random.randint(0, ROWS - 1) * TILE_SIZE

        occupied = False
        if x == snake_head.x and y == snake_head.y:
            occupied = True

        for part in snake_body:
            if part.x == x and part.y == y:
                occupied = True
                break

        if not occupied:
            food.x = x
            food.y = y
            return


def reset_game():
    global snake_head, snake_body, velocity_x, velocity_y, score, game_over

    snake_head = Tile(5 * TILE_SIZE, 5 * TILE_SIZE)
    snake_body = []
    velocity_x = 0
    velocity_y = 0
    score = 0
    game_over = False

    spawn_food()
    draw()


def change_dir(e):
    global velocity_x, velocity_y

    key = e.keysym.lower()

    # Handle restart if game is over
    if game_over:
        if key == "space":
            reset_game()
        return

    if key in ("up", "w") and velocity_y != 1:
        velocity_x = 0
        velocity_y = -1

    elif key in ("down", "s") and velocity_y != -1:
        velocity_x = 0
        velocity_y = 1

    elif key in ("left", "a") and velocity_x != 1:
        velocity_x = -1
        velocity_y = 0

    elif key in ("right", "d") and velocity_x != -1:
        velocity_x = 1
        velocity_y = 0


def move():
    global game_over, score

    if game_over:
        return

    if velocity_x == 0 and velocity_y == 0:
        return

    old_head_x = snake_head.x
    old_head_y = snake_head.y

    snake_head.x += velocity_x * TILE_SIZE
    snake_head.y += velocity_y * TILE_SIZE

    if (
        snake_head.x < 0
        or snake_head.x >= WINDOW_WIDTH
        or snake_head.y < 0
        or snake_head.y >= WINDOW_HEIGHT
    ):
        game_over = True
        return

    if snake_body:
        for i in range(len(snake_body) - 1, 0, -1):
            snake_body[i].x = snake_body[i - 1].x
            snake_body[i].y = snake_body[i - 1].y

        snake_body[0].x = old_head_x
        snake_body[0].y = old_head_y

    for part in snake_body:
        if snake_head.x == part.x and snake_head.y == part.y:
            game_over = True
            return

    if snake_head.x == food.x and snake_head.y == food.y:
        snake_body.append(Tile(old_head_x, old_head_y))
        score += 1
        spawn_food()


def draw():
    move()

    canvas.delete("all")

    # Grid
    for x in range(0, WINDOW_WIDTH, TILE_SIZE):
        canvas.create_line(x, 0, x, WINDOW_HEIGHT, fill="#222222")

    for y in range(0, WINDOW_HEIGHT, TILE_SIZE):
        canvas.create_line(0, y, WINDOW_WIDTH, y, fill="#222222")

    # Border
    canvas.create_rectangle(
        1, 1, WINDOW_WIDTH - 2, WINDOW_HEIGHT - 2, outline="lime", width=2
    )

    # Food
    canvas.create_oval(
        food.x + 4,
        food.y + 4,
        food.x + TILE_SIZE - 4,
        food.y + TILE_SIZE - 4,
        fill="red",
        outline="",
    )

    # Body
    for part in snake_body:
        canvas.create_rectangle(
            part.x + 1,
            part.y + 1,
            part.x + TILE_SIZE - 1,
            part.y + TILE_SIZE - 1,
            fill="#1a8f1a",
            outline="",
        )

    # Head
    canvas.create_rectangle(
        snake_head.x + 1,
        snake_head.y + 1,
        snake_head.x + TILE_SIZE - 1,
        snake_head.y + TILE_SIZE - 1,
        fill="lime",
        outline="",
    )

    # Score
    canvas.create_text(
        50, 18, text=f"Score: {score}", fill="white", font=("Arial", 12, "bold")
    )

    if game_over:
        canvas.create_text(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2,
            text=f"GAME OVER\n\nFinal Score: {score}\n\nPress SPACE to Restart",
            fill="yellow",
            font=("Arial", 24, "bold"),
            justify="center",
        )
    else:
        root.after(100, draw)

# Draws directly on the same canvas the game uses, driven by root.after,
# so it never blocks the mainloop and always hands off cleanly into the game.

PETAL_COUNT = 8
FRAMES_PER_PETAL = 9        # frames it takes one petal to fully grow
FRAME_DELAY = 28            # ms between animation frames
PETAL_LENGTH = 65
PETAL_WIDTH = 26
CENTER_RADIUS = 16
TEXT_FRAMES = 26            # frames for the title/subtitle/prompt to fade in

CX = WINDOW_WIDTH / 2
CY = WINDOW_HEIGHT / 2 - 40   # nudge flower up a bit so text fits below it

TOTAL_BLOOM_FRAMES = PETAL_COUNT * FRAMES_PER_PETAL


def hsv_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, s, v)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def petal_points(angle_deg, growth):
    """Build a rotated petal polygon (list of (x, y) canvas coords).
    growth (0..1) controls how far the petal has extended from the center."""
    length = PETAL_LENGTH * growth
    angle = math.radians(angle_deg)
    steps = 14

    top = []
    for i in range(steps + 1):
        t = i / steps
        x = t * length
        w = (PETAL_WIDTH / 2) * math.sin(math.pi * t)
        top.append((x, w))
    bottom = [(x, -w) for x, w in reversed(top)]
    local_pts = top + bottom

    pts = []
    for x, y in local_pts:
        rx = x * math.cos(angle) - y * math.sin(angle)
        ry = x * math.sin(angle) + y * math.cos(angle)
        pts.append((CX + rx, CY + ry))
    return pts


def draw_flower(bloom_frame):
    """Draws all petals at their current growth state for a given frame count."""
    for i in range(PETAL_COUNT):
        angle = i * (360 / PETAL_COUNT) - 90  # start pointing up
        petal_start_frame = i * FRAMES_PER_PETAL
        local_frame = bloom_frame - petal_start_frame

        if local_frame <= 0:
            continue  # this petal hasn't started growing yet

        growth = min(1.0, local_frame / FRAMES_PER_PETAL)
        color = "white"

        pts = petal_points(angle, growth)
        flat_pts = [coord for point in pts for coord in point]
        canvas.create_polygon(flat_pts, fill=color, outline="", smooth=True)


def draw_center_and_stem():
    # Flower center
    canvas.create_oval(
        CX - CENTER_RADIUS, CY - CENTER_RADIUS,
        CX + CENTER_RADIUS, CY + CENTER_RADIUS,
        fill="black", outline="white", width=1,
    )


def draw_intro(frame=0):
    canvas.delete("all")

    bloom_frame = min(frame, TOTAL_BLOOM_FRAMES)
    draw_flower(bloom_frame)

    if frame >= TOTAL_BLOOM_FRAMES:
        draw_center_and_stem()

        text_frame = frame - TOTAL_BLOOM_FRAMES
        text_progress = min(1.0, text_frame / (TEXT_FRAMES * 0.5))
        font_size = max(1, int(30 * text_progress))

        canvas.create_text(
            CX, CY + 185,
            text="EXTRACT GAMES",
            fill="lime",
            font=("Courier", font_size, "bold"),
            justify="center",
        )

        if text_frame > TEXT_FRAMES * 0.4:
            canvas.create_text(
                CX, CY + 215,
                text="Your Favourite Tkinter Game Making Dude",
                fill="gray",
                font=("Courier", 11, "normal"),
            )

        if text_frame > TEXT_FRAMES * 0.75:
            canvas.create_text(
                CX, WINDOW_HEIGHT - 15,
                text="Press any key to begin",
                fill="white",
                font=("Arial", 12, "bold"),
            )

    total_frames = TOTAL_BLOOM_FRAMES + TEXT_FRAMES
    if frame < total_frames:
        root.after(FRAME_DELAY, draw_intro, frame + 1)
    elif frame == total_frames:
        # Intro fully drawn - hold it on screen for 3 seconds before starting the game
        root.after(3000, start_game)


def start_game():
    spawn_food()
    root.bind("<Key>", change_dir)
    draw()

draw_intro()
root.mainloop()
