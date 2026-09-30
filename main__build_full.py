import pygame
import random
import math
import sys

pygame.init()
WIDTH, HEIGHT = 960, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("osu!megamix")
clock = pygame.time.Clock()

FONT_BIG = pygame.font.SysFont("Arial", 48)
FONT = pygame.font.SysFont("Arial", 24)

# Timing constants (milliseconds)
HIT_WINDOW_300 = 50
HIT_WINDOW_100 = 100
HIT_WINDOW_50 = 150
MISS_WINDOW = 200

APPROACH_TIME = 1000  # AR baseline

MAX_HEALTH = 100

# -----------------------------
# Circle Object
# -----------------------------

class Circle:
    def __init__(self):
        self.x = random.randint(150, WIDTH - 150)
        self.y = random.randint(150, HEIGHT - 150)
        self.spawn_time = pygame.time.get_ticks()
        self.hit = False
        self.result = None

    def time_since_spawn(self):
        return pygame.time.get_ticks() - self.spawn_time

    def draw(self):
        t = self.time_since_spawn()

        # Approach circle
        approach_scale = max(0, 1 - (t / APPROACH_TIME))
        approach_radius = int(80 + 120 * approach_scale)
        pygame.draw.circle(screen, (100,100,255),
                           (self.x, self.y),
                           approach_radius, 2)

        # Hit circle
        pygame.draw.circle(screen, (255,255,255),
                           (self.x, self.y),
                           40, 3)

    def judge(self):
        t = abs(self.time_since_spawn() - APPROACH_TIME)

        if t <= HIT_WINDOW_300:
            return 300
        elif t <= HIT_WINDOW_100:
            return 100
        elif t <= HIT_WINDOW_50:
            return 50
        elif t <= MISS_WINDOW:
            return 0
        return None

    def expired(self):
        return self.time_since_spawn() > APPROACH_TIME + MISS_WINDOW


# -----------------------------
# Game State
# -----------------------------

def reset_game():
    return {
        "circles": [],
        "score": 0,
        "combo": 0,
        "max_combo": 0,
        "health": MAX_HEALTH,
        "last_spawn": 0,
        "spawn_interval": 800,
        "running": True,
    }

def title_screen():
    while True:
        screen.fill((0,0,0))
        title = FONT_BIG.render("osu!megamix", True, (255,255,255))
        sub = FONT.render("Press 1: Standard   2: Mania   ESC: Quit", True, (180,180,180))

        screen.blit(title, (WIDTH//2 - title.get_width()//2, 200))
        screen.blit(sub, (WIDTH//2 - sub.get_width()//2, 300))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    return "standard"
                if event.key == pygame.K_2:
                    return "mania"
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()


# -----------------------------
# Standard Mode
# -----------------------------

def play_standard():
    state = reset_game()

    while state["running"]:
        dt = clock.tick(60)
        now = pygame.time.get_ticks()

        screen.fill((30,30,40))

        # spawn logic
        if now - state["last_spawn"] > state["spawn_interval"]:
            state["circles"].append(Circle())
            state["last_spawn"] = now

        # health drain
        state["health"] -= 0.02 * dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state["circles"]:
                    circle = state["circles"][0]
                    result = circle.judge()

                    if result is not None:
                        if result > 0:
                            state["combo"] += 1
                            state["max_combo"] = max(state["combo"], state["max_combo"])
                            state["score"] += result * state["combo"]
                            state["health"] += result / 10
                        else:
                            state["combo"] = 0
                            state["health"] -= 15

                        state["circles"].pop(0)

        # expire check
        for circle in state["circles"][:]:
            if circle.expired():
                state["combo"] = 0
                state["health"] -= 20
                state["circles"].remove(circle)

        # draw
        for circle in state["circles"]:
            circle.draw()

        # UI
        pygame.draw.rect(screen, (60,0,0),
                         (20,20,200,20))
        pygame.draw.rect(screen, (0,200,0),
                         (20,20,int(200*(state["health"]/MAX_HEALTH)),20))

        score_text = FONT.render(f"Score: {state['score']}", True, (255,255,255))
        combo_text = FONT.render(f"Combo: {state['combo']}", True, (255,255,0))

        screen.blit(score_text, (20,60))
        screen.blit(combo_text, (20,90))

        pygame.display.flip()

        if state["health"] <= 0:
            return


# -----------------------------
# Mania Mode (Keyboard Lanes)
# -----------------------------

def play_mania():
    state = reset_game()
    lanes = 4
    lane_width = WIDTH // lanes
    keys = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
    notes = []

    class Note:
        def __init__(self, lane):
            self.lane = lane
            self.y = -40
            self.speed = 5

        def update(self):
            self.y += self.speed

        def draw(self):
            x = lane_width * self.lane + lane_width//2
            pygame.draw.rect(screen, (200,200,255),
                             (x-20, self.y, 40, 40))

    spawn_timer = 0

    while True:
        dt = clock.tick(60)
        spawn_timer += dt
        screen.fill((20,20,20))

        if spawn_timer > 600:
            notes.append(Note(random.randint(0, lanes-1)))
            spawn_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key in keys:
                    lane = keys.index(event.key)
                    for note in notes:
                        if note.lane == lane and HEIGHT-100 < note.y < HEIGHT-40:
                            state["score"] += 300
                            state["combo"] += 1
                            state["health"] += 5
                            notes.remove(note)
                            break
                    else:
                        state["combo"] = 0
                        state["health"] -= 10

        for note in notes[:]:
            note.update()
            if note.y > HEIGHT:
                notes.remove(note)
                state["combo"] = 0
                state["health"] -= 15

        # draw lanes
        for i in range(lanes):
            pygame.draw.line(screen, (80,80,80),
                             (lane_width*i,0),
                             (lane_width*i,HEIGHT),2)

        for note in notes:
            note.draw()

        pygame.display.flip()

        if state["health"] <= 0:
            return


# -----------------------------
# Main Loop
# -----------------------------

while True:
    mode = title_screen()

    if mode == "standard":
        play_standard()
    elif mode == "mania":
        play_mania()

