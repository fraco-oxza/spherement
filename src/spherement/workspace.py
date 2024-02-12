from __future__ import annotations
from enum import Enum

import math
from typing import Optional
from tkinter import filedialog

import pygame


def ask_file() -> Optional[str]:
    file_path = filedialog.askopenfilename()
    return file_path


class DrawPoint:
    angle: float
    distance: float

    def __init__(self, angle: float, distance: float):
        self.angle = angle
        self.distance = distance

    def get_indexes(self) -> tuple[float, float]:
        return (
            self.distance * math.cos(self.angle),
            -self.distance * math.sin(self.angle),
        )

    @staticmethod
    def from_indexes(indexes: tuple[float, float] | list[float]) -> DrawPoint:
        x, y = indexes
        return DrawPoint(math.atan2(-y, x), math.sqrt(x**2 + y**2))

    @staticmethod
    def from_point_2d(point: Point2d) -> DrawPoint:
        return DrawPoint.from_indexes((point.x, point.y))

    def __mul__(self, other: float) -> DrawPoint:
        return DrawPoint(self.angle, self.distance * other)

    def __rmul__(self, other: float) -> DrawPoint:
        return self * other

    def __add__(self, other: DrawPoint) -> DrawPoint:
        x1, y1 = self.get_indexes()
        x2, y2 = other.get_indexes()
        return DrawPoint.from_indexes((x1 + x2, y1 + y2))

    def __sub__(self, other: DrawPoint) -> DrawPoint:
        x1, y1 = self.get_indexes()
        x2, y2 = other.get_indexes()
        return DrawPoint.from_indexes((x1 - x2, y1 - y2))

    def __iadd__(self, other: DrawPoint) -> DrawPoint:
        return self + other


class Point2d:
    x: float
    y: float

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance(self, p: Point2d):
        return math.sqrt((self.x - p.x) ** 2 + (self.y - p.y) ** 2)

    def module(self):
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> Point2d:
        module = self.module()
        return Point2d(self.x / module, self.y / module)

    def get_indexes(self) -> tuple[float, float]:
        return (self.x, self.y)

    @staticmethod
    def add_points(points: list[Point2d]) -> Point2d:
        x = sum([p.x for p in points])
        y = sum([p.y for p in points])
        return Point2d(x, y)

    @staticmethod
    def from_draw_point(draw_point: DrawPoint) -> Point2d:
        return Point2d(*draw_point.get_indexes())

    def __mul__(self, other: float) -> Point2d:
        return Point2d(self.x * other, self.y * other)

    def __rmul__(self, other: float) -> Point2d:
        return self * other


class Point3d:
    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        self.x = x
        self.y = y
        self.z = z

    def distance(self, p: Point3d):
        return math.sqrt(
            (self.x - p.x) ** 2 + (self.y - p.y) ** 2 + (self.z - p.z) ** 2
        )

    def module(self):
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> Point3d:
        module = self.module()
        return Point3d(self.x / module, self.y / module, self.z / module)


class Line:
    p1: Point3d
    p2: Point3d

    def __init__(self, p1: Point3d, p2: Point3d):
        self.p1 = p1
        self.p2 = p2

    def angle(self):
        return 2.0 * math.asin(self.p1.normalize().distance(self.p2.normalize()) / 2.0)


class Stage(Enum):
    ADJUSTMENT = 0
    MEASUREMENT = 1


class Workspace:
    top: int
    left: int
    height: int
    width: int
    image: Optional[pygame.Surface]
    image_pos: DrawPoint
    image_offset: Point2d
    scale: float
    radius: float
    view_point: Point2d
    points: list[DrawPoint]
    stage: Stage

    def __init__(self, top: int, left: int, width: int, height: int):
        self.top = top
        self.left = left
        self.height = height
        self.width = width
        self.image = None
        self.scale = 1
        self.view_point = Point2d(0, 0)
        self.image_offset = Point2d(0, 0)
        self.radius = min(self.width, self.height) / 2
        self.points = []
        self.stage = Stage.ADJUSTMENT
        self.center = Point2d(self.width / 2, self.height / 2)

    def set_image(self, image: pygame.Surface):
        self.image = image
        self.view_point = Point2d(0, 0)
        self.scale = 1.0

    def to_local_coords(self, coord: list[int] | tuple[int, int]) -> Point2d:
        return Point2d(coord[0] - self.left, coord[1] - self.top)

    def pov(self):
        return Point2d.add_points([self.view_point, self.center])

    def draw(self, screen: pygame.Surface):
        surf = pygame.Surface((self.width, self.height))
        pygame.draw.rect(surf, "#434343", (0, 0, self.width, self.height))

        if self.image:
            surf.blit(
                pygame.transform.scale_by(self.image, self.scale),
                Point2d.add_points(
                    [self.scale * self.image_offset, self.pov()]
                ).get_indexes(),
            )

        circle_radius = self.radius * (
            self.scale if self.stage is Stage.MEASUREMENT else 1.0
        )
        pygame.draw.circle(
            surf,
            "#00FF00",
            self.pov().get_indexes(),
            circle_radius,
            1,
        )

        for draw_point in self.points:
            pygame.draw.circle(
                surf,
                "#FF0000",
                Point2d.add_points(
                    [self.pov(), Point2d.from_draw_point(self.scale * draw_point)]
                ).get_indexes(),
                5,
            )

        # Iter over pair points and calculate and show angular distance
        for pair in range(0, len(self.points) - 1, 2):
            p1 = self.points[pair]
            p2 = self.points[pair + 1]

            pygame.draw.line(
                surf,
                "#FF0000",
                Point2d.add_points(
                    [self.pov(), Point2d.from_draw_point(self.scale * p1)]
                ).get_indexes(),
                Point2d.add_points(
                    [self.pov(), Point2d.from_draw_point(self.scale * p2)]
                ).get_indexes(),
                1,
            )

            p1_x, p1_y = p1.get_indexes()
            p1_x, p1_y = p1_x / self.radius, p1_y / self.radius
            p1_3d = Point3d(p1_x, p1_y, math.sqrt(1 - p1_x**2 - p1_y**2))

            p2_x, p2_y = p2.get_indexes()
            p2_x, p2_y = p2_x / self.radius, p2_y / self.radius
            p2_3d = Point3d(p2_x, p2_y, math.sqrt(1 - p2_x**2 - p2_y**2))

            print(
                "LINE Nº ",
                pair,
                ":",
                p1_3d.x,
                p1_3d.y,
                p1_3d.z,
                " - ",
                p2_3d.x,
                p2_3d.y,
                p2_3d.z,
            )

            angle = math.degrees(Line(p1_3d, p2_3d).angle())
            font = pygame.font.Font(None, 24)
            text = font.render(f"{angle:.2f}", True, "#FF0000", "#ffff00")

            # write in the center of the line
            surf.blit(
                text,
                Point2d.add_points(
                    [
                        self.pov(),
                        Point2d.from_draw_point(
                            DrawPoint.from_indexes(
                                (
                                    (p1.get_indexes()[0] + p2.get_indexes()[0]) / 2,
                                    (p1.get_indexes()[1] + p2.get_indexes()[1]) / 2,
                                )
                            )
                            * self.scale
                        ),
                        Point2d(-10, -10),
                    ]
                ).get_indexes(),
            )

        screen.blit(surf, (self.left, self.top))

    def change_scale(self, delta: float):
        if not self.image:
            return

        p = DrawPoint.from_point_2d(self.view_point)
        self.view_point = Point2d.from_draw_point(p * delta)
        self.scale *= delta

    def move_view(self):
        keys = pygame.key.get_pressed()

        multiplier = 1.0
        if keys[pygame.K_LSHIFT]:
            multiplier = 5.0

        if keys[pygame.K_UP]:
            self.view_point.y += 1 * self.scale * multiplier
        if keys[pygame.K_DOWN]:
            self.view_point.y -= 1 * self.scale * multiplier
        if keys[pygame.K_LEFT]:
            self.view_point.x += 1 * self.scale * multiplier
        if keys[pygame.K_RIGHT]:
            self.view_point.x -= 1 * self.scale * multiplier
        if keys[pygame.K_MINUS]:
            self.change_scale(0.99**multiplier)
        if keys[pygame.K_PLUS]:
            self.change_scale(1.01**multiplier)
        if keys[pygame.K_SPACE]:
            image_path = ask_file()
            if image_path:
                self.set_image(pygame.image.load(image_path))

    def add_point(self, events: list[pygame.event.Event]):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.points.append(
                        DrawPoint.from_point_2d(
                            Point2d.add_points(
                                [
                                    self.to_local_coords(event.pos),
                                    -1 * self.view_point,
                                    -1 * self.center,
                                ],
                            ),
                        )
                        * (1 / self.scale)
                    )

                    if self.points[-1].distance > self.radius:
                        self.points.pop()
                        print("Point out of range")

                elif event.button == 3:
                    self.points.pop()

    def adjust_view(self, events: list[pygame.event.Event]):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.image_offset.y += 1
        if keys[pygame.K_DOWN]:
            self.image_offset.y -= 1
        if keys[pygame.K_LEFT]:
            self.image_offset.x += 1
        if keys[pygame.K_RIGHT]:
            self.image_offset.x -= 1
        if keys[pygame.K_MINUS]:
            self.change_scale(0.99)
        if keys[pygame.K_PLUS]:
            self.change_scale(1.01)

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.image is not None:
                        self.stage = Stage.MEASUREMENT
                        self.image = pygame.transform.scale_by(self.image, self.scale)
                        h, w = self.image.get_size()
                        self.image_offset.x += (h / self.scale - h) / 2
                        self.image_offset.y += (w / self.scale - w) / 2
                        self.scale = 1.0

    def update(self, events: list[pygame.event.Event]):
        if not self.image:
            file = ask_file()
            if file is not None:
                self.set_image(pygame.image.load(file))
        if self.stage == Stage.ADJUSTMENT and True:
            self.adjust_view(events)
        elif self.stage == Stage.MEASUREMENT:
            self.move_view()
            self.add_point(events)
