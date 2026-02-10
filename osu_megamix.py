import pygame, time, sys, random

# ---------------- SETUP ----------------
pygame.init()
WIDTH, HEIGHT = 900, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("osu!megamix - random jam")
clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 20)

# ---------------- CLOCK ----------------
class GameClock:
    def __init__(self):
        self.start = time.time()
    def now(self):
        return time.time() - self.start

# ---------------- BASE MODE ----------------
class BaseMode:
    name = "base"
    def reset(self): pass
    def update(self, t): pass
    def draw(self): pass
    def handle(self, e, t): pass

# =========================================================
# osu!standard - random circles
# SPACE to hit
# =========================================================
class StandardMode(BaseMode):
    name = "osu"
    HIT_WINDOW = 0.15

    def reset(self):
        self.clock = GameClock()
        self.circles = []
        self.last_spawn = 0
        self.judge = ""
        self.score = 0

    def update(self, t):
        # spawn random circles every 1–2 seconds
        if t - self.last_spawn > random.uniform(1, 2):
            self.circles.append({"time": t + 2.0, "hit": False})
            self.last_spawn = t

        for c in self.circles:
            if not c["hit"] and t - c["time"] > self.HIT_WINDOW:
                c["hit"] = True
                self.judge = "MISS"

    def draw(self):
        screen.fill((0,0,0))
        for c in self.circles:
            if c["hit"]: continue
            # spawn ahead (2 sec travel)
            t = self.clock.now()
            x = WIDTH//2
            y = HEIGHT//2
            pygame.draw.circle(screen, (255,100,100), (x, y), 40, 4)
        screen.blit(FONT.render(f"{self.judge} Score:{self.score}", True, (255,255,0)), (10,10))

    def handle(self, e, t):
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
            for c in self.circles:
                if not c["hit"] and abs(t - c["time"]) <= self.HIT_WINDOW:
                    c["hit"] = True
                    self.judge = "GOOD"
                    self.score += 300
                    return
            self.judge = "MISS"

# =========================================================
# TAIKO - random notes
# F/J = Don, D/K = Kat
# =========================================================
class TaikoMode(BaseMode):
    name = "taiko"
    HIT_X = 150
    SPEED = 300
    HIT_WINDOW = 0.15

    def reset(self):
        self.clock = GameClock()
        self.notes = []
        self.last_spawn = 0
        self.judge = ""
        self.score = 0

    def update(self, t):
        # spawn random don/kat notes every 0.5–1.2 sec
        if t - self.last_spawn > random.uniform(0.5,1.2):
            kind = random.choice(["don","kat"])
            self.notes.append({"time": t + 2.0, "type": kind, "hit": False})
            self.last_spawn = t

        for n in self.notes:
            if not n["hit"] and t - n["time"] > self.HIT_WINDOW:
                n["hit"] = True
                self.judge = "MISS"

    def draw(self):
        screen.fill((0,0,0))
        pygame.draw.line(screen,(255,255,255),(self.HIT_X,250),(WIDTH,250),2)
        pygame.draw.line(screen,(255,100,100),(self.HIT_X,220),(self.HIT_X,280),4)

        t = self.clock.now()
        for n in self.notes:
            if n["hit"]: continue
            x = self.HIT_X + (n["time"] - t) * self.SPEED
            if x < -40 or x > WIDTH: continue
            color = (255,80,80) if n["type"] == "don" else (80,80,255)
            pygame.draw.circle(screen, color, (int(x),250), 18)

        screen.blit(FONT.render(f"{self.judge} Score:{self.score}", True, (255,255,0)), (10,10))

    def try_hit(self, kind):
        t = self.clock.now()
        for n in self.notes:
            if not n["hit"] and n["type"] == kind and abs(t - n["time"]) <= self.HIT_WINDOW:
                n["hit"] = True
                self.judge = "GOOD"
                self.score += 300
                return
        self.judge = "MISS"

    def handle(self, e, t):
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_f, pygame.K_j): self.try_hit("don")
            if e.key in (pygame.K_d, pygame.K_k): self.try_hit("kat")

# =========================================================
# MANIA 4K - random notes
# D F J K
# =========================================================
class ManiaMode(BaseMode):
    name = "mania"
    SPEED = 350
    HIT_Y = 420
    HIT_WINDOW = 0.15

    def reset(self):
        self.clock = GameClock()
        self.notes = []
        self.last_spawn = 0
        self.judge = ""
        self.score = 0

    def update(self, t):
        if t - self.last_spawn > random.uniform(0.5,1.0):
            lane = random.randint(0,3)
            self.notes.append({"time": t + 2.0, "lane": lane, "hit": False})
            self.last_spawn = t

        for n in self.notes:
            if not n["hit"] and t - n["time"] > self.HIT_WINDOW:
                n["hit"] = True
                self.judge = "MISS"

    def draw(self):
        screen.fill((0,0,0))
        lane_w = 100
        for i in range(4):
            pygame.draw.rect(screen,(40,40,40),(200+i*lane_w,0,lane_w,HEIGHT))
            pygame.draw.line(screen,(255,255,255),(200+i*lane_w,self.HIT_Y),(200+(i+1)*lane_w,self.HIT_Y),2)

        t = self.clock.now()
        for n in self.notes:
            if n["hit"]: continue
            y = self.HIT_Y - (n["time"] - t) * self.SPEED
            if 0 < y < HEIGHT:
                pygame.draw.rect(screen,(200,100,200),(200+n["lane"]*lane_w,y, lane_w,20))

        screen.blit(FONT.render(f"{self.judge} Score:{self.score}", True, (255,255,0)), (10,10))

    def handle(self, e, t):
        keys = [pygame.K_d, pygame.K_f, pygame.K_j, pygame.K_k]
        if e.type == pygame.KEYDOWN and e.key in keys:
            lane = keys.index(e.key)
            for n in self.notes:
                if not n["hit"] and n["lane"] == lane and abs(t - n["time"]) <= self.HIT_WINDOW:
                    n["hit"] = True
                    self.judge = "GOOD"
                    self.score += 300
                    return
            self.judge = "MISS"

# =========================================================
# CTB - random fruits
# LEFT / RIGHT
# =========================================================
class CTBMode(BaseMode):
    name = "ctb"

    def reset(self):
        self.clock = GameClock()
        self.x = WIDTH//2
        self.fruits = []
        self.last_spawn = 0
        self.judge = ""
        self.score = 0

    def update(self, t):
        # spawn fruit every 0.5–1.2 sec
        if t - self.last_spawn > random.uniform(0.5,1.2):
            self.fruits.append({"x": random.randint(50, WIDTH-50), "y":0})
            self.last_spawn = t

        for f in self.fruits:
            f["y"] += 4
            if f["y"] > HEIGHT-40 and abs(f["x"] - self.x) < 40:
                self.judge = "CATCH"
                self.score += 300
                f["y"] = -100

    def draw(self):
        screen.fill((0,0,0))
        pygame.draw.rect(screen,(100,255,100),(self.x-40,HEIGHT-30,80,20))
        for f in self.fruits:
            pygame.draw.circle(screen,(255,0,0),(f["x"],int(f["y"])),15)
        screen.blit(FONT.render(f"{self.judge} Score:{self.score}", True, (255,255,0)), (10,10))

    def handle(self, e, t):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: self.x -= 6
        if keys[pygame.K_RIGHT]: self.x += 6

# ---------------- MODE HUB ----------------
MODES = {
    pygame.K_1: StandardMode,
    pygame.K_2: TaikoMode,
    pygame.K_3: ManiaMode,
    pygame.K_4: CTBMode,
}

mode = StandardMode()
mode.reset()

# ---------------- MAIN LOOP ----------------
while True:
    t = mode.clock.now()

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()
            if e.key in MODES:
                mode = MODES[e.key]()
                mode.reset()
        mode.handle(e, t)

    mode.update(t)
    mode.draw()
    screen.blit(FONT.render(f"Mode: {mode.name} (1–4)", True, (255,255,255)), (10, HEIGHT-25))
    pygame.display.flip()
    clock.tick(60)

