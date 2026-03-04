import pygame
import sys
import time

# stub aubio
aubio = None
def get_onsets_stub(audio_data=None):
    return [1000, 2000, 3000, 4000, 5000]  # fixed test timings

# initialize pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("osu!Megamix Phase 1")
clock = pygame.time.Clock()

# stub game objects
CIRCLE_RADIUS = 30
circle_positions = [(100, 100), (300, 200), (500, 400), (700, 300)]
hit_keys = {"z": False, "x": False}

# main loop
start_time = pygame.time.get_ticks()
running = True
while running:
    screen.fill((30, 30, 30))  # background

    # draw circles
    for pos in circle_positions:
        pygame.draw.circle(screen, (255, 100, 100), pos, CIRCLE_RADIUS)

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                hit_keys["z"] = True
            elif event.key == pygame.K_x:
                hit_keys["x"] = True
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_z:
                hit_keys["z"] = False
            elif event.key == pygame.K_x:
                hit_keys["x"] = False

    # show pressed keys
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Z: {hit_keys['z']}  X: {hit_keys['x']}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

