#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
osu!Megamix Phase 1 — playable prototype
- pygame window
- stubbed aubio
- Z/X hit detection
"""

import pygame
import sys

# ---------------------------
# STUBS / HEADLESS
# ---------------------------
aubio = None
def get_onsets_stub(audio_data=None):
    return [1000, 2000, 3000, 4000, 5000]  # ms timestamps for test circles

# ---------------------------
# PYGAME SETUP
# ---------------------------
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("osu!Megamix Phase 1")
clock = pygame.time.Clock()

# ---------------------------
# GAME OBJECTS
# ---------------------------
CIRCLE_RADIUS = 30
circle_positions = [(100, 100), (300, 200), (500, 400), (700, 300)]
hit_keys = {"z": False, "x": False}

# ---------------------------
# MAIN LOOP
# ---------------------------
running = True
while running:
    screen.fill((30, 30, 30))  # dark background

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

    # display key state
    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Z: {hit_keys['z']}  X: {hit_keys['x']}", True, (255, 255, 255))
    screen.blit(text, (10, 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()

