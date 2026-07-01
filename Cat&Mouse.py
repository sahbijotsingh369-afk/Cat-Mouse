import random
import tkinter as tk
import colorsys
import math

# ------------------------------------------------------------
root = tk.Tk()
root.resizable(False, False)
root.title("Cat & Mouse")
root.configure(bg="black")

fullscreen = False

def toggle_fullscreen(event=None):
    global fullscreen
    fullscreen = not fullscreen
    root.attributes("-fullscreen", fullscreen)

def exit_fullscreen(event=None):
    global fullscreen
    fullscreen = False
    root.attributes("-fullscreen", False)

# F11 = Toggle Fullscreen
root.bind("<F11>", toggle_fullscreen)

# Escape = Exit Fullscreen
root.bind("<Escape>", exit_fullscreen)

ROWS = 25
COL = 25
TILE_SIZE = 25

WINDOW_WIDTH = TILE_SIZE * COL
WINDOW_HEIGHT = TILE_SIZE * ROWS


class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# Green border frame
border = tk.Frame(root, bg="lime")
border.pack()

# Added padding to expose the green border underneath
canvas = tk.Canvas(
    border,
    bg="#111111",
    highlightthickness=0,
    width=WINDOW_WIDTH,
    height=WINDOW_HEIGHT,
)
canvas.pack(padx=2, pady=2)
root.update()

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

window_x = int((screen_width / 2) - (WINDOW_WIDTH / 2))
window_y = int((screen_height / 2) - (WINDOW_HEIGHT / 2))

# Added 4 pixels to geometry to accommodate the 2px border on all sides
root.geometry(f"{WINDOW_WIDTH + 4}x{WINDOW_HEIGHT + 4}+{window_x}+{window_y}")

# ---------------- GAME STATE ----------------

player = Tile(5 * TILE_SIZE, 5 * TILE_SIZE)

target = Tile(
    random.randint(0, COL - 1) * TILE_SIZE,
    random.randint(0, ROWS - 1) * TILE_SIZE,
)

enemy = Tile(
    random.randint(0, COL - 1) * TILE_SIZE,
    random.randint(0, ROWS - 1) * TILE_SIZE,
)

# Prevent spawning on the player
while (target.x == player.x and target.y == player.y) or (
    enemy.x == player.x and enemy.y == player.y
) or (enemy.x == target.x and enemy.y == target.y):
    target = Tile(
        random.randint(0, COL - 1) * TILE_SIZE,
        random.randint(0, ROWS - 1) * TILE_SIZE,
    )
    enemy = Tile(
        random.randint(0, COL - 5) * TILE_SIZE,
        random.randint(0, ROWS - 5) * TILE_SIZE,
    )

velocity_x = 0
velocity_y = 0

score = 0
game_over = False
game_started = False  # Track if player made their first move

stop_job = None

def reset_game():
    global player, target, enemy
    global velocity_x, velocity_y
    global score, game_over, game_started
    global stop_job

    # Cancel pending stop timer
    if stop_job is not None:
        root.after_cancel(stop_job)
        stop_job = None

    player = Tile(5 * TILE_SIZE, 5 * TILE_SIZE)

    target = Tile(
        random.randint(0, COL - 1) * TILE_SIZE,
        random.randint(0, ROWS - 1) * TILE_SIZE,
    )

    enemy = Tile(
        random.randint(0, COL - 1) * TILE_SIZE,
        random.randint(0, ROWS - 1) * TILE_SIZE,
    )

    # Prevent overlapping spawns
    while (
        (target.x == player.x and target.y == player.y)
        or (enemy.x == player.x and enemy.y == player.y)
        or (enemy.x == target.x and enemy.y == target.y)
    ):
        target = Tile(
            random.randint(0, COL - 1) * TILE_SIZE,
            random.randint(0, ROWS - 1) * TILE_SIZE,
        )
        enemy = Tile(
            random.randint(0, COL - 1) * TILE_SIZE,
            random.randint(0, ROWS - 1) * TILE_SIZE,
        )

    velocity_x = 0
    velocity_y = 0
    score = 0
    game_over = False
    game_started = False

    draw()

# ---------------- INPUT ----------------

def change_dir(e):
    global velocity_x, velocity_y, stop_job, game_started

    key = e.keysym.lower()

    # Restart when game is over
    if game_over:
        if key == "space":
            reset_game()
        return

    if key in ("up", "w"):
        velocity_x = 0
        velocity_y = -1
    elif key in ("down", "s"):
        velocity_x = 0
        velocity_y = 1
    elif key in ("left", "a"):
        velocity_x = -1
        velocity_y = 0
    elif key in ("right", "d"):
        velocity_x = 1
        velocity_y = 0
    else:
        return

    if stop_job is not None:
        root.after_cancel(stop_job)

    stop_job = root.after(100, stop_movement)

    # Start enemy movement loop only on the first move
    if not game_started:
        game_started = True
        move_enemy()

def stop_movement():
    global velocity_x, velocity_y
    velocity_x = 0
    velocity_y = 0

# ---------------- ENEMY AI ----------------

def move_enemy():
    global game_over

    if game_over:
        return

    dx = player.x - enemy.x
    dy = player.y - enemy.y

    if abs(dx) >= abs(dy):
        if dx > 0:
            enemy.x += TILE_SIZE
        elif dx < 0:
            enemy.x -= TILE_SIZE
    else:
        if dy > 0:
            enemy.y += TILE_SIZE
        elif dy < 0:
            enemy.y -= TILE_SIZE

    if enemy.x == player.x and enemy.y == player.y:
        game_over = True

    root.after(400, move_enemy)

# ---------------- PLAYER LOGIC ----------------

def move():
    global game_over, score

    if game_over:
        return

    if velocity_x == 0 and velocity_y == 0:
        return

    next_x = player.x + velocity_x * TILE_SIZE
    next_y = player.y + velocity_y * TILE_SIZE

    # Wall collision
    if (
        next_x < 0
        or next_x >= WINDOW_WIDTH
        or next_y < 0
        or next_y >= WINDOW_HEIGHT
    ):
        game_over = True
        return

    player.x = next_x
    player.y = next_y

    # Collect gold oval
    if player.x == target.x and player.y == target.y:
        score += 1

        while True:
            target.x = random.randint(0, COL - 1) * TILE_SIZE
            target.y = random.randint(0, ROWS - 1) * TILE_SIZE

            if (
                (target.x != player.x or target.y != player.y)
                and (target.x != enemy.x or target.y != enemy.y)
            ):
                break

    # Enemy collision
    if player.x == enemy.x and player.y == enemy.y:
        game_over = True

# ---------------- DRAW ----------------

def draw():
    move()

    canvas.delete("all")

    # Clean inner grid lines matching your variables
    for x in range(TILE_SIZE, WINDOW_WIDTH, TILE_SIZE):
        canvas.create_line(x, 0, x, WINDOW_HEIGHT, fill="#222222")

    for y in range(TILE_SIZE, WINDOW_HEIGHT, TILE_SIZE):
        canvas.create_line(0, y, WINDOW_WIDTH, y, fill="#222222")

    # Collectible (Gold)
    canvas.create_oval(
        target.x + 2,
        target.y + 2,
        target.x + TILE_SIZE - 2,
        target.y + TILE_SIZE - 2,
        fill="gold",
        outline="",
    )

    # Enemy (Red)
    canvas.create_rectangle(
        enemy.x + 1,
        enemy.y + 1,
        enemy.x + TILE_SIZE - 1,
        enemy.y + TILE_SIZE - 1,
        fill="Red",
        outline="",
    )

    # Player (Green)
    canvas.create_rectangle(
        player.x + 1,
        player.y + 1,
        player.x + TILE_SIZE - 1,
        player.y + TILE_SIZE - 1,
        fill="lime green",
        outline="",
    )

    canvas.create_text(
        55,
        20,
        text=f"Score: {score}",
        fill="white",
        font=("Arial", 12, "bold"),
    )

    if game_over:
        canvas.create_text(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2,
            text=f"GAME OVER\nFinal Score: {score}",
            fill="yellow",
            font=("Arial", 24, "bold"),
            justify="center",
        )
        canvas.create_text(
            WINDOW_WIDTH / 2,
            WINDOW_HEIGHT / 2 + 70,
            text="Press SPACE to Restart",
            fill="white",
            font=("Arial", 14, "bold"),
        )
    if not game_over:
        root.after(100, draw)

# ---------------- INTRO ANIMATION: blooming flower (canvas-based, non-blocking) ----------------
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
                text="Cat & Mouse",
                fill="gray",
                font=("Courier", 11, "normal"),
            )

        if text_frame > TEXT_FRAMES * 0.75:
            canvas.create_text(
                CX, WINDOW_HEIGHT - 15,
                text="-----x-----",
                fill="white",
                font=("Arial", 12, "bold"),
            )

    total_frames = TOTAL_BLOOM_FRAMES + TEXT_FRAMES
    if frame < total_frames:
        root.after(FRAME_DELAY, draw_intro, frame + 1)
    elif frame == total_frames:

        root.after(3000, start_game)


def start_game():
    """Called once the intro finishes; wires up input and starts the game loop."""
    root.bind("<Key>", change_dir)
    draw()

# ---------------- START ----------------

draw_intro()
root.mainloop()
# ---------------------------------------------------------------------------------