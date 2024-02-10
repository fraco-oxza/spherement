import math

from spherement.workspace import DrawPoint, Line, Point

EPSILON = 1e-12


def test_point_module():
    p = Point(5, 7, 6)
    assert p.module() == math.sqrt(5**2 + 7**2 + 6**2)


def test_angle():
    p1 = Point(-4, 3, 1)
    p2 = Point(3, -4, 4)

    o = Line(p1, p2)

    assert abs(o.angle() - math.radians(127.7751208134)) < EPSILON


def test_draw_point():
    p1 = 2 * DrawPoint.from_indexes((3, 4))
    p2 = DrawPoint.from_indexes((6, 8))

    assert (
        p1.get_indexes() == p2.get_indexes()
        and p1.distance == p2.distance == 10.0
        and abs(p1.angle - p2.angle) < EPSILON
        and abs(p1.angle - math.asin(-4 / 5)) < EPSILON
    )
