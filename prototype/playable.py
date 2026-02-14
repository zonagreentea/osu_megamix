import pygame
import random
import time
import sys

# -------- config --------
WIDTH, HEIGHT = 800, 600
FPS = 60
CIRCLE_RADIUS = 40
APPROACH_TIME = 1.2  # seconds before hit
HIT_WINDOW = 0.15   # seconds
BG = (15, 15, 20)
CIRCLE = (120, 180, 255)
APPROACH = (200, 200, 200)
TEXT = (240, 240, 240)

# -------- init --------
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("osu!megamix — prototype")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 28)

# -------- state --------
circles = []
score = 0
running = True

def spawn_circle():
    return {
        "pos": (
            random.randint(100, WIDTH - 100),
            random.randint(100, HEIGHT - 100),
        ),
        "time": time.time() + APPROACH_TIME,
        "hit": False,
    }

circles.append(spawn_circle())

# -------- loop --------
while running:
    now = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_z, pygame.K_x):
                for c in circles:
                    if c["hit"]:
                        continue
                    dt = abs(now - c["time"])
                    if dt <= HIT_WINDOW:
                        c["hit"] = True
                        score += 300
                        break

    # auto-miss cleanup
    circles = [
        c for c in circles
        if not (now - c["time"] > HIT_WINDOW and not c["hit"])
    ]

    if len(circles) < 3:
        circles.append(spawn_circle())

    # -------- draw --------
    screen.fill(BG)

    for c in circles:
        t = c["time"] - now
        if t > -HIT_WINDOW:
            scale = max(1.0, t / APPROACH_TIME)
            pygame.draw.circle(
                screen,
                APPROACH,
                c["pos"],
                int(CIRCLE_RADIUS * scale),
                2,
            )
            pygame.draw.circle(
                screen,
                CIRCLE,
                c["pos"],
                CIRCLE_RADIUS,
            )

    score_text = font.render(f"Score: {score}", True, TEXT)
    screen.blit(score_text, (20, 20))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

