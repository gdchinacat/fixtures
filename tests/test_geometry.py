# mypy: disable-error-code=no-untyped-call
# mypy: disable-error-code=untyped-decorator

import abc
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass
import math
import unittest
from types import NotImplementedType
from typing import Any

from fixtures import kwargs


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


###
# Now that the data model classes have been defined, create the kwargs
# factories for them.
###
_Circle = kwargs.factory(Circle)
_Point = kwargs.factory(Point)


class Tests(unittest.TestCase):

    @ kwargs["origin"] << _Point(0, 0)
    @ kwargs["outer"] << _Circle(3, center=kwargs["origin"])
    @ kwargs["inner"] << _Circle(2, center=kwargs["origin"])
    @ kwargs["disjoint"] << _Circle(5, center=Point(10, 10))
    def test_circle_overlap(
        self, outer: Circle, inner: Circle, disjoint: Circle, **_: Any
    ) -> None:
        self.assertTrue(outer.overlaps(inner))
        self.assertTrue(inner.overlaps(outer))
        self.assertTrue(outer.overlaps(outer))
        self.assertFalse(disjoint.overlaps(inner))
        self.assertFalse(outer.overlaps(disjoint))
