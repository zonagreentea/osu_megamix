#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
osu!Megamix Phase 1 Build
- pygame window
- auto-generated circles
- Z/X hit detection
- score display
- headless / aubio stub
"""

import pygame
import sys
import time

# ---------------------------
# STUBS
# ---------------------------
aubio = None
def get_onsets_stub(audio_data=None):
    # auto-timed hits every 1 second
    return [1000 * i for i in range(1, 21)]

# ---------------------------
# PYGAME SETUP
# ---------------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("osu!Megamix Phase 1 Build")
clock = pygame.time.Clock()

# ---------------------------
# GAME OBJECTS
# ---------------------------
CIRCLE_RADIUS = 30
circle_positions = []  # will spawn dynamically
spawn_times = get_onsets_stub()
hit_keys = {"z": False, "x": False}
score = 0
font = pygame.font.SysFont(None, 36)

# ---------------------------
# MAIN LOOP
# ---------------------------
start_time = pygame.time.get_ticks()
running = True

while running:
    current_time = pygame.time.get_ticks() - start_time

    # spawn circles based on timeline
    for t in spawn_times:
        if current_time >= t and len(circle_positions) < len(spawn_times):
            x = 100 + (len(circle_positions) * 100)
            y = 100 + (len(circle_positions) * 50 % 400)
            circle_positions.append((x, y))

    # handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                hit_keys["z"] = True
                score += 10
            elif event.key == pygame.K_x:
                hit_keys["x"] = True
                score += 10
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_z:
                hit_keys["z"] = False
            elif event.key == pygame.K_x:
                hit_keys["x"] = False

    # draw
    screen.fill((30, 30, 30))
    for pos in circle_positions:
        pygame.draw.circle(screen, (255, 100, 100), pos, CIRCLE_RADIUS)

    # display score and keys
    text = font.render(f"Score: {score}  Z: {hit_keys['z']}  X: {hit_keys['x']}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

