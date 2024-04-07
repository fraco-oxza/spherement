"""
This module contains the classes to represent the workspace of the application.
The workspace is the area where the image is shown and the points are added.
"""

from __future__ import annotations
from enum import Enum

import math
from typing import Optional

import pygame


class DrawPoint:
    """
    A point in the screen with polar coordinates
    """

    angle: float
    distance: float

    def __init__(self, angle: float, distance: float):
        """
        Create a new DrawPoint
        """
        self.angle = angle
        self.distance = distance

    def get_indexes(self) -> tuple[float, float]:
        """
        Return the cartesian coordinates of the point
        """
        return (
            self.distance * math.cos(self.angle),
            -self.distance * math.sin(self.angle),
        )

    @staticmethod
    def from_indexes(indexes: tuple[float, float] | list[float]) -> DrawPoint:
        """
        Create a new DrawPoint from cartesian coordinates
        """
        x, y = indexes
        return DrawPoint(math.atan2(-y, x), math.hypot(x, y))

    @staticmethod
    def from_point_2d(point: Point2d) -> DrawPoint:
        """
        Create a new DrawPoint from a Point2d
        """
        return DrawPoint.from_indexes((point.x, point.y))

    def __mul__(self, other: float) -> DrawPoint:
        """
        Multiply the distance of the point by a scalar
        """
        return DrawPoint(self.angle, self.distance * other)

    def __rmul__(self, other: float) -> DrawPoint:
        """
        Multiply the distance of the point by a scalar
        """
        return self * other

    def __add__(self, other: DrawPoint) -> DrawPoint:
        """
        Add two points
        """
        x1, y1 = self.get_indexes()
        x2, y2 = other.get_indexes()
        return DrawPoint.from_indexes((x1 + x2, y1 + y2))

    def __sub__(self, other: DrawPoint) -> DrawPoint:
        """
        Subtract two points
        """
        x1, y1 = self.get_indexes()
        x2, y2 = other.get_indexes()
        return DrawPoint.from_indexes((x1 - x2, y1 - y2))

    def __iadd__(self, other: DrawPoint) -> DrawPoint:
        """
        Add two points
        """
        return self + other


class Point2d:
    """
    A point in the plane with cartesian coordinates. Axis y is inverted to
    match the screen coordinates
    """

    x: float
    y: float

    def __init__(self, x: float, y: float):
        """
        Create a new Point2d
        """
        self.x = x
        self.y = y

    def distance(self, p: Point2d):
        """
        Return the distance between two points
        """
        return math.sqrt((self.x - p.x) ** 2 + (self.y - p.y) ** 2)

    def module(self):
        """
        Return the module of the vector
        """
        return math.sqrt(self.x**2 + self.y**2)

    def normalize(self) -> Point2d:
        """
        Return the unit vector of the vector.
        """
        module = self.module()
        return Point2d(self.x / module, self.y / module)

    def get_indexes(self) -> tuple[float, float]:
        """
        Return the cartesian coordinates of the point
        """
        return (self.x, self.y)

    @staticmethod
    def add_points(points: list[Point2d]) -> Point2d:
        """
        Return the sum of a list of points
        """
        x = sum(p.x for p in points)
        y = sum(p.y for p in points)
        return Point2d(x, y)

    @staticmethod
    def from_draw_point(draw_point: DrawPoint) -> Point2d:
        """
        Create a new Point2d from a DrawPoint
        """
        return Point2d(*draw_point.get_indexes())

    def __mul__(self, other: float) -> Point2d:
        """
        Multiply the coordinates of the point by a scalar
        """
        return Point2d(self.x * other, self.y * other)

    def __rmul__(self, other: float) -> Point2d:
        """
        Multiply the coordinates of the point by a scalar
        """
        return self * other


class Point3d:
    """
    A point in the space with cartesian coordinates
    """

    x: float
    y: float
    z: float

    def __init__(self, x: float, y: float, z: float):
        """Create a new Point3d"""
        self.x = x
        self.y = y
        self.z = z

    def distance(self, p: Point3d):
        """Return the distance between two points"""
        return math.sqrt(
            (self.x - p.x) ** 2 + (self.y - p.y) ** 2 + (self.z - p.z) ** 2
        )

    def module(self):
        """Return the module of the vector"""
        return math.sqrt(self.x**2 + self.y**2 + self.z**2)

    def normalize(self) -> Point3d:
        """Return the unit vector of the vector."""
        module = self.module()
        return Point3d(self.x / module, self.y / module, self.z / module)

    def get_angle_to(self, p: Point3d) -> float:
        """
        Return the angle between two vectors. The angle is in radians and it's
        the angle between the two vectors that start in the origin and end in
        the points.
        """
        return 2.0 * math.asin(self.normalize().distance(p.normalize()) / 2.0)


class Stage(Enum):
    """Enum to define the stage of the workspace"""

    ADJUSTMENT = 0
    MEASUREMENT = 1


class DrawBox:
    """
    A box in the screen. It's used to draw the workspace
    """

    top: int
    left: int
    height: int
    width: int
    center: Point2d
    radius: float

    def __init__(self, top: int, left: int, width: int, height: int):
        self.top = top
        self.left = left
        self.height = height
        self.width = width
        self.center = Point2d(width / 2, height / 2)
        self.radius = min(width, height) / 2

    def to_local_coords(self, coord: list[int] | tuple[int, int]) -> Point2d:
        """
        Transform the screen coordinates to the local coordinates. thats means
        that the origin is the top-left corner of the image and the y-axis is
        inverted.
        """
        return Point2d(coord[0] - self.left, coord[1] - self.top)

    def get_surface(self) -> pygame.Surface:
        """Return a surface with the size of the box"""
        surf = pygame.Surface((self.width, self.height))
        surf.fill("#282828")
        return surf


class Workspace:
    """
    The workspace of the application. It contains the image and the points
    """

    area: DrawBox
    image: Optional[pygame.Surface]
    image_pos: DrawPoint
    image_offset: Point2d
    scale: float
    circle_diff: float
    view_point: Point2d
    points: list[DrawPoint]
    stage: Stage

    def __init__(self, padding: int, side: int):
        """
        Create a new Workspace
        """
        self.area = DrawBox(padding, padding, side, side)
        self.image = None
        self.scale = 1.0
        self.view_point = Point2d(0, 0)
        self.image_offset = Point2d(0, 0)
        self.points = []
        self.stage = Stage.ADJUSTMENT
        self.circle_diff = 0.0

    def set_image(self, image: pygame.Surface):
        """Set the image of the workspace"""
        self.image = image
        self.view_point = Point2d(0, 0)
        self.scale = 1.0

    def pov(self):
        """Return the point of view of the workspace"""
        return Point2d.add_points([self.view_point, self.area.center])

    def draw_points_and_distances(self, surf: pygame.Surface):
        """
        Draw the points and the distances between them in the screen
        """
        for pair in range(0, len(self.points) - 1, 2):
            p1 = self.points[pair]
            p2 = self.points[pair + 1]

            pygame.draw.line(
                surf,
                "#fb4934",
                Point2d.add_points(
                    [self.pov(), Point2d.from_draw_point(self.scale * p1)]
                ).get_indexes(),
                Point2d.add_points(
                    [self.pov(), Point2d.from_draw_point(self.scale * p2)]
                ).get_indexes(),
                1,
            )

            p1_x, p1_y = (p1 * (1 / self.area.radius)).get_indexes()
            p1_3d = Point3d(p1_x, p1_y, math.sqrt(1 - p1_x**2 - p1_y**2))

            p2_x, p2_y = (p2 * (1 / self.area.radius)).get_indexes()
            p2_3d = Point3d(p2_x, p2_y, math.sqrt(1 - p2_x**2 - p2_y**2))

            angle = math.degrees(p1_3d.get_angle_to(p2_3d))
            font = pygame.font.Font("fonts/Roboto-Regular.ttf", 20)
            text = font.render(f" {angle:.2f}º ", True, "#ebdbb2", "#141617")

            # write in the center of the line
            surf.blit(
                text,
                Point2d.add_points(
                    [
                        self.pov(),
                        Point2d.from_draw_point((p1 + p2) * 0.5 * self.scale),
                        Point2d(*text.get_size()) * -0.5,
                    ]
                ).get_indexes(),
            )

    def draw(self, screen: pygame.Surface):
        """Draw the workspace in the screen"""
        surf = self.area.get_surface()

        if self.image:
            surf.blit(
                pygame.transform.scale_by(self.image, self.scale + self.circle_diff),
                Point2d.add_points(
                    [(self.scale + self.circle_diff) * self.image_offset, self.pov()]
                ).get_indexes(),
            )

        circle_radius = self.area.radius * (
            (self.scale) if self.stage is Stage.MEASUREMENT else 1.0
        )
        pygame.draw.circle(
            surf,
            "#b8bb26",
            self.pov().get_indexes(),
            circle_radius,
            1,
        )

        for draw_point in self.points:
            pygame.draw.circle(
                surf,
                "#fb4934",
                Point2d.add_points(
                    [self.pov(), Point2d.from_draw_point(self.scale * draw_point)]
                ).get_indexes(),
                5,
            )

        self.draw_points_and_distances(surf)

        screen.blit(surf, (self.area.left, self.area.top))

    def change_scale(self, delta: float):
        """
        Change the scale of the image. The scale is the factor that multiplies
        the size of the image. Also change the view point to keep the same point
        in the center of the screen.
        """
        p = DrawPoint.from_point_2d(self.view_point)
        self.view_point = Point2d.from_draw_point(p * delta)
        self.scale *= delta
        self.circle_diff *= delta

    def move_view(self):
        """
        Move the view point of the workspace. The view point is the point that
        is in the center of the screen.
        """
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

    def add_point(self, events: list[pygame.event.Event]):
        """
        Add a point to the workspace. The point is added when the left button
        of the mouse is pressed. The point is removed when the right button is
        pressed.
        """
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self.points.append(
                        DrawPoint.from_point_2d(
                            Point2d.add_points(
                                [
                                    self.area.to_local_coords(event.pos),
                                    -1 * self.view_point,
                                    -1 * self.area.center,
                                ],
                            ),
                        )
                        * (1 / self.scale)
                    )

                    if self.points[-1].distance > self.area.radius:
                        self.points.pop()
                        print("Point out of range")

                elif event.button == 3:
                    self.points.pop()

    def adjust_view(self, events: list[pygame.event.Event]):
        """
        Adjust the view of the workspace. The view is adjusted with the arrow
        keys and the plus and minus keys. The view is changed in the x and y
        axis and the scale of the image is changed.
        """
        keys = pygame.key.get_pressed()

        multiplier = 1.0
        if keys[pygame.K_LSHIFT]:
            multiplier = 5.0

        if keys[pygame.K_UP]:
            self.image_offset.y += 1 * multiplier
        if keys[pygame.K_DOWN]:
            self.image_offset.y -= 1 * multiplier
        if keys[pygame.K_LEFT]:
            self.image_offset.x += 1 * multiplier
        if keys[pygame.K_RIGHT]:
            self.image_offset.x -= 1 * multiplier
        if keys[pygame.K_MINUS]:
            self.change_scale(0.99**multiplier)
        if keys[pygame.K_PLUS]:
            self.change_scale(1.01**multiplier)

        for event in events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.stage = Stage.MEASUREMENT
                self.circle_diff = self.scale - 1.0
                self.scale = 1.0

    def update(self, events: list[pygame.event.Event]):
        """
        Update the workspace. The workspace is updated depending on the stage
        """
        if self.stage == Stage.ADJUSTMENT:
            self.adjust_view(events)
        elif self.stage == Stage.MEASUREMENT:
            self.move_view()
            self.add_point(events)
