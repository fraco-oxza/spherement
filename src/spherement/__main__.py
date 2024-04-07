import sys

import pygame

from spherement.workspace import Workspace


RESOLUTION = 800
MARGIN = 20
WORKSPACE_SIZE = RESOLUTION - 2 * MARGIN


class Shperement:
    def __init__(self):
        self.screen = pygame.display.set_mode((RESOLUTION, RESOLUTION))
        self.clock = pygame.time.Clock()
        self.running = True
        self.events = []
        self.workspace = Workspace(MARGIN, WORKSPACE_SIZE)

    def process_events(self):
        self.events = pygame.event.get()
        if any(event.type == pygame.QUIT for event in self.events):
            self.running = False

    def set_image(self, image):
        image = pygame.image.load(image)
        self.workspace.set_image(image)

    def draw(self):
        self.screen.fill("#232323")
        self.workspace.draw(self.screen)

    def run(self) -> None:
        while self.running:
            self.process_events()
            self.workspace.update(self.events)
            self.draw()

            pygame.display.flip()
            self.clock.tick(60)


if __name__ == "__main__":
    pygame.init()

    spherement = Shperement()
    spherement.set_image(sys.argv[1])
    spherement.run()
