import pygame, time, random, math

pygame.init()
W, H = 800, 600
screen = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()

# timing
APPROACH_TIME = 1.0  # seconds before hit
HIT_WINDOW_300 = 0.08
HIT_WINDOW_100 = 0.16

notes = []
score = 0

start_time = time.time()

def gromp_signal(t):
    return math.sin(t*2) + math.sin(t*0.7) + random.uniform(-0.2,0.2)

def spawn_note():
    t = time.time() - start_time
    g = gromp_signal(t)

    x = int((g + 2)/4 * (W-100)) + 50
    y = random.randint(100, H-100)

    hit_time = time.time() + APPROACH_TIME

    # random slider or circle
    if random.random() < 0.3:
        length = random.randint(100, 200)
        return {
            "type": "slider",
            "x": x, "y": y,
            "length": length,
            "hit_time": hit_time,
            "duration": 0.6,
            "hit": False
        }
    else:
        return {
            "type": "circle",
            "x": x, "y": y,
            "hit_time": hit_time,
            "hit": False
        }

spawn_timer = 0

running = True
while running:
    dt = clock.tick(60)/1000
    now = time.time()

    spawn_timer += dt
    if spawn_timer > 0.5:
        notes.append(spawn_note())
        spawn_timer = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            for n in notes:
                if n["hit"]:
                    continue

                dx = mx - n["x"]
                dy = my - n["y"]
                dist = math.hypot(dx, dy)

                if dist < 40:
                    diff = abs(now - n["hit_time"])

                    if diff < HIT_WINDOW_300:
                        score += 300
                        print("300")
                    elif diff < HIT_WINDOW_100:
                        score += 100
                        print("100")
                    else:
                        print("miss")

                    if n["type"] == "circle":
                        n["hit"] = True
                    else:
                        n["holding"] = True
                        n["hold_start"] = now

    screen.fill((10,10,15))

    for n in notes:
        if n["hit"]:
            continue

        time_left = n["hit_time"] - now

        # remove missed
        if time_left < -0.3:
            n["hit"] = True
            continue

        # approach circle
        scale = max(0, time_left / APPROACH_TIME)
        radius = int(40 + scale * 80)

        pygame.draw.circle(screen, (100,100,255), (n["x"], n["y"]), radius, 2)

        # main hit circle
        pygame.draw.circle(screen, (255,255,255), (n["x"], n["y"]), 40)

        if n["type"] == "slider":
            end_x = n["x"] + n["length"]
            pygame.draw.line(screen, (200,200,200),
                             (n["x"], n["y"]),
                             (end_x, n["y"]), 5)

            # slider ball
            if "holding" in n:
                progress = min(1, (now - n["hold_start"]) / n["duration"])
                ball_x = n["x"] + progress * n["length"]
                pygame.draw.circle(screen, (255,200,100),
                                   (int(ball_x), n["y"]), 15)

                if progress >= 1:
                    score += 200
                    n["hit"] = True

    # UI
    font = pygame.font.SysFont(None, 36)
    txt = font.render(f"Score: {score}", True, (255,255,255))
    screen.blit(txt, (10,10))

    pygame.display.flip()

pygame.quit()
