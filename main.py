from enum import Enum
from typing import Optional
import math

import pygame
import tkinter as tk
from tkinter import filedialog

MARGIN = 20
WIDTH = 1280
HEIGHT = 720
PANEL_WIDTH = 300
DEV_MODE = not True
# DELTA_SCALE = 0.01
SCALE_MULTIPLIER = 1.01
SURF_SIZE = (WIDTH - 3 * MARGIN - PANEL_WIDTH, HEIGHT - 2 * MARGIN)
RADIUS = min(SURF_SIZE) / 2


class AppProcess(Enum):
    SELECT_IMAGE = 1
    MARK_CIRCLE = 2
    DISTANCE_MESURE = 3


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
running = True
root = tk.Tk()
root.withdraw()
image: Optional[pygame.Surface] = None
image_pos = [0.0, 0.0]
scale = [1.0, 1.0]
zoom = 1.0
circle_center = [0.0, 0.0]
actual_process = AppProcess.SELECT_IMAGE


def process_events():
    global running, scale, zoom
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_UP]:
        if keys[pygame.K_LSHIFT]:
            if actual_process == AppProcess.DISTANCE_MESURE:
                zoom *= SCALE_MULTIPLIER

                angle = math.atan2(circle_center[1], -circle_center[0])
                mov = (math.hypot(circle_center[0], circle_center[1])) * (
                    1.0 - 1.0 / SCALE_MULTIPLIER
                )

                d0 = mov * math.cos(angle)
                d1 = mov * math.sin(angle)

                circle_center[0] -= d0
                circle_center[1] += d1
                image_pos[0] -= d0
                image_pos[1] += d1
            else:
                scale[1] /= SCALE_MULTIPLIER
        else:
            image_pos[1] += 1 * zoom
            if actual_process == AppProcess.DISTANCE_MESURE:
                circle_center[1] += 1.0 * zoom
    if keys[pygame.K_DOWN]:
        if keys[pygame.K_LSHIFT]:
            if actual_process == AppProcess.DISTANCE_MESURE:
                zoom /= SCALE_MULTIPLIER

                angle = math.atan2(circle_center[1], -circle_center[0])
                mov = (math.hypot(circle_center[0], circle_center[1])) * (
                    1.0 - SCALE_MULTIPLIER
                )

                d0 = mov * math.cos(angle)
                d1 = mov * math.sin(angle)

                circle_center[0] -= d0
                circle_center[1] += d1
                image_pos[0] -= d0
                image_pos[1] += d1

            else:
                scale[1] *= SCALE_MULTIPLIER
        else:
            image_pos[1] -= 1.0 * zoom
            if actual_process == AppProcess.DISTANCE_MESURE:
                circle_center[1] -= 1.0 * zoom
    if keys[pygame.K_LEFT]:
        if keys[pygame.K_LSHIFT]:
            if actual_process != AppProcess.DISTANCE_MESURE:
                scale[0] /= SCALE_MULTIPLIER
        else:
            image_pos[0] += 1.0 * zoom
            if actual_process == AppProcess.DISTANCE_MESURE:
                circle_center[0] += 1.0 * zoom
    if keys[pygame.K_RIGHT]:
        if keys[pygame.K_LSHIFT]:
            if actual_process != AppProcess.DISTANCE_MESURE:
                scale[0] *= SCALE_MULTIPLIER
        else:
            image_pos[0] -= 1.0 * zoom
            if actual_process == AppProcess.DISTANCE_MESURE:
                circle_center[0] -= 1.0 * zoom


def draw_background():
    screen.fill("#232323")


def draw_main_surface():
    surf = pygame.Surface(SURF_SIZE)
    surf.fill("#434343")

    if image is not None:
        image_scaled = pygame.transform.scale_by(
            image, [*map(lambda x: x * zoom, scale)]
        )
        image_size = image_scaled.get_size()
        surf.blit(
            image_scaled,
            (
                SURF_SIZE[0] / 2
                + image_pos[0]
                - image_size[0] / 2
                + (image_pos[0] - circle_center[0]) * (zoom - 1),
                SURF_SIZE[1] / 2
                + image_pos[1]
                - image_size[1] / 2
                + (image_pos[1] - circle_center[1]) * (zoom - 1),
            ),
        )

    pygame.draw.circle(
        surf,
        "#ff0000",
        (SURF_SIZE[0] / 2 + circle_center[0], SURF_SIZE[1] / 2 + circle_center[1]),
        RADIUS * zoom,
        2,
    )

    pygame.draw.circle(
        surf,
        "#ffff00",
        (SURF_SIZE[0] / 2, SURF_SIZE[1] / 2),
        3,
    )

    screen.blit(surf, (MARGIN, MARGIN))


while running:
    process_events()
    draw_background()
    draw_main_surface()

    if actual_process == AppProcess.SELECT_IMAGE:
        if image is None:
            file_path = (
                filedialog.askopenfilename() if not DEV_MODE else "./HMI_week.jpg"
            )
            if file_path:
                image = pygame.image.load(file_path)
                actual_process = AppProcess.MARK_CIRCLE
            else:
                running = False
    elif actual_process == AppProcess.MARK_CIRCLE:
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            actual_process = AppProcess.DISTANCE_MESURE
    elif actual_process == AppProcess.DISTANCE_MESURE:
        print(circle_center[1] / (RADIUS * zoom), -circle_center[0] / (RADIUS * zoom))

    pygame.display.flip()
    clock.tick(60)
