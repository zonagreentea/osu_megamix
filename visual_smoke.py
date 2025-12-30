import math, time, sys
import pygame

# Hottest pink imaginable (electric magenta)
HOT_PINK = (255, 0, 255)     # #FF00FF
DEEP_PINK = (255, 20, 147)   # #FF1493

W, H = 960, 540
FPS = 60

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("osu!megamix • visual smoke • HOT PINK")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Menlo", 22) or pygame.font.Font(None, 22)

t0 = time.time()
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False
        if e.type == pygame.KEYDOWN and e.key in (pygame.K_ESCAPE, pygame.K_q):
            running = False

    t = time.time() - t0

    # CALMER background
    screen.fill(DEEP_PINK)

    # Slower pulse
    cx, cy = W//2, H//2
    r = int(40 + 120 * (0.5 + 0.5 * math.sin(t * 1.1)))
    thickness = 10
    pygame.draw.circle(screen, (0, 0, 0), (cx, cy), r + 3, thickness + 6)
    pygame.draw.circle(screen, HOT_PINK, (cx, cy), r, thickness)

    msg = "VISUALS: ONLINE  •  ESC/Q to quit"
    txt = font.render(msg, True, (0, 0, 0))
    screen.blit(txt, (24, 24))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit(0)
