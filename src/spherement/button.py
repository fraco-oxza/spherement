from typing import Optional

import pygame


class Button:
    top: int
    left: int
    width: int
    height: int
    text: Optional[str] = None
    hover: bool = False

    def __init__(self, top, left, width, height):
        self.top = top
        self.left = left
        self.width = width
        self.height = height

    def set_text(self, text):
        self.text = text

    def is_inside(self, x, y):
        return (
            self.left <= x <= self.left + self.width
            and self.top <= y <= self.top + self.height
        )

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_inside(*event.pos):
                print("Button clicked!")

    def update(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self.hover = self.is_inside(*event.pos)
        # self.hover = self.is_inside(*pygame.mouse.get_pos())

    def draw(self, surface):
        if self.hover:
            pygame.draw.rect(
                surface, "#00ff00", (self.left, self.top, self.width, self.height)
            )
        else:
            pygame.draw.rect(
                surface, "#ff0000", (self.left, self.top, self.width, self.height)
            )
