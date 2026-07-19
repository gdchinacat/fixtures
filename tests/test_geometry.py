# mypy: disable-error-code=no-untyped-call
# mypy: disable-error-code=untyped-decorator

import abc
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
import math
import unittest
from types import NotImplementedType
from typing import Any

from fixtures import fixture


@dataclass(config=ConfigDict(extra="allow"))
class Shape(abc.ABC):
    def overlaps(self, other: Shape) -> bool:
        raise NotImplementedError(
            f"{type(self)}.overlaps({type(other)}) not implemented"
        )


@dataclass
class Point(Shape):
    x: int
    y: int

    def overlaps(self, other: Shape) -> bool:
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        if isinstance(other, Circle):
            return other.overlaps(self)
        return super().overlaps(other)


@dataclass
class Circle(Shape):
    radius: float
    center: Point

    def overlaps(self, other: Shape) -> bool | NotImplementedType:
        if isinstance(other, Circle):
            dist = math.hypot(
                self.center.x - other.center.x, self.center.y - other.center.y
            )
            return dist <= self.radius + other.radius
        if isinstance(other, Point):
            dist = math.hypot(self.center.x - other.x, self.center.y - other.y)
            return dist <= self.radius
        return super().overlaps(other)


class Tests(unittest.TestCase):

    @fixture(Point, 0, 0, fixture_name="origin")
    @fixture(Circle, 3, center=fixture.kwargs["origin"], fixture_name="outer")
    @fixture(Circle, 2, center=fixture.kwargs["origin"], fixture_name="inner")
    @fixture(Circle, 5, center=Point(10, 10), fixture_name="other")
    def test_circle_overlap(
        self, outer: Circle, inner: Circle, other: Circle, **_: Any
    ) -> None:
        self.assertTrue(outer.overlaps(inner))
        self.assertTrue(inner.overlaps(outer))
        self.assertTrue(outer.overlaps(outer))
        self.assertFalse(other.overlaps(inner))
        self.assertFalse(outer.overlaps(other))
