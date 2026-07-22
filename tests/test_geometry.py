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
# TODO - this is really ugly:
#    1) The datamodel must use non-factories for references between classes, so
#       the classes can't themselves be decorated with @kwargs.factory.
#    2) kwargs decorators must use factories
#         it could be spelled:
#            @ kwargs["origin"] << kwargs.factory(Point)(0, 0)
#         but that seems worse and creates massive bloat unless they are
#         interned.
#    3) the factory looks like a Point, but isn't a point, so the decorated
#       function will be typed differently:
#       @ kwargs['origim'] << Point(1, 1)
#       def test_origin(origin: model.Point): ...
#
#  In practice, how ugly is it, really? The models are likely to already be
#  defined elsewhere (in the code being tested) so:
#      Point = kwargs.factory(model.Point)
#  would likely be the 'proper' way to do it, which is alright(?).
#
#  This wasn't an issue with original @fixture(...) because it didn't create
#  partial factories, it just held the factory and kwargs.
#    1) the partial factory is 'needed' to disambiguate factory from kwarg
#       from literal. It could assume any callable is a factory, but that is
#       implicit (and explicit is better).
#    2) the '<<< Point(1)' syntax is more readable (IMO) than '(Point, 1)'.
#
#  If the factories explicitly supported currying by creating a curried object
#  that was detectable in the same way _FactoryPartial is this could be
#  improved, but I don't want to require datamodels be extended from things
#  that are just for test code. The test code shouldn't be in production and
#  testing with it and shipping without is a Bad Idea.
#
#  So, what to do?
#    1) different syntax rather than isinstance?
#        @ kwargs['foo'] == literal_value # or kwargs['bar']
#        @ kwargs['foo'] << (Point, 1)
#    2) ???
#
#  For now, targets must be factories...Yuck.
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
