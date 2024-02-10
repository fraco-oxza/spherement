from enum import Enum
from typing import Optional
import math

import pygame
import tkinter as tk


from spherement.workspace import Workspace

RESOLUTION = (1280, 720)
MARGIN = 20
WORKSPACE_SIZE = (
    int(2 * (RESOLUTION[0] / 3) - 2 * MARGIN),
    int(RESOLUTION[1] - 2 * MARGIN),
)

tk.Tk().withdraw()


class Shperement:
    def __init__(self):
        self.screen = pygame.display.set_mode(RESOLUTION)
        self.clock = pygame.time.Clock()
        self.running = True
        self.events = []
        self.workspace = Workspace(MARGIN, MARGIN, *WORKSPACE_SIZE)

    def process_events(self):
        self.events = pygame.event.get()
        if any(event.type == pygame.QUIT for event in self.events):
            self.running = False

    def draw(self):
        self.screen.fill("#232323")
        self.workspace.draw(self.screen)

    def update(self):
        self.workspace.update(self.events)

    def run(self) -> None:
        while self.running:
            self.process_events()
            self.update()
            self.draw()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    pygame.init()
    Shperement().run()
