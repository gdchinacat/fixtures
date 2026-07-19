__all__ = ("fixture", "default_fixture_name", "get_default_fixture_name")

from functools import wraps
from itertools import count
import os
from random import randint
from unittest import TestCase

from typing import Callable, ParamSpec, TypeVar, Any

type Factory[**P, R] = Callable[P, R]
type Function[**P, R] = Callable[P, R]

_DEFAULT_FIXTURE_NAME_ATTR = "__default_fixture_name"


def default_fixture_name[**P, R](
    name: str,
) -> Callable[[Factory[P, R]], Factory[P, R]]:
    """
    Decorator to set the default fixture name for a factory.

    The original tests rely on get_default_fixture_name(factory) to refer to
    the kwarg name the fixture should be injected under. We store the name
    on the factory object.
    """

    def _decorator(func: Factory[P, R]) -> Factory[P, R]:
        if hasattr(func, _DEFAULT_FIXTURE_NAME_ATTR):
            raise AttributeError
        setattr(func, _DEFAULT_FIXTURE_NAME_ATTR, name)
        return func

    return _decorator


def get_default_fixture_name[**P, R](factory: Factory[P, R]) -> str:
    """
    Return the default fixture name for a factory.

    Fall back to the lower cased factory __name__if no explicit name was
    provided. It is lower case so idiomatic class names become idiomatic
    argument named (ie foo is used for factory/class Foo).
    """
    return getattr(
        factory, _DEFAULT_FIXTURE_NAME_ATTR, factory.__name__.lower()
    )


class _KwargSubstitution:
    """
    A kwarg value that indicates to @fixture to replace it with the value of
    another kwarg. Used to map kwargs in the fixture stack to kwargs the
    factory function needs.
    Not used directly, rather use foo=fixture.kwargs['bar'] to pass a kwarg
    named foo with a value the kwarg 'bar' has. Both foo and bar will be
    kwargs to the factory function.
    """

    def __init__(self, kwarg: str = "") -> None:
        self.kwarg = kwarg

    @classmethod
    def __getitem__(cls, kwarg: str) -> _KwargSubstitution:
        """create a kwarg substitution token"""
        return cls(kwarg)

    @staticmethod
    def _substitute_kwargs(
        fixture_kwargs: dict[str, object], kwargs: dict[str, object]
    ) -> dict[str, object]:
        return {
            k: kwargs[v.kwarg] if isinstance(v, _KwargSubstitution) else v
            for k, v in fixture_kwargs.items()
        }


# Type annotations are intentionally missing since python type annotations do
# not support adding kwargs and it is not possible to properly type this
# functionality.
class fixture:
    """
    fixture is a decorator that is used to call functions and inject the return
    value as a keyword argument into the call to the decorate function. It can
    be stacked to create many objects to pass to the decorated function. This
    is useful for creating fixtures for tests.
    While this can all be done in the test function itself this allows the
    setup for the test to be clearly separated from the test action and
    validation. This separation makes it easier to see what the initial state
    of the test is and makes it easier to reuse test setup.
    While 'explicit is better than implicit', many of the transient variables
    to hold fixtures are eliminated from the code through good naming (TODO
    add an example).

    ###
    # data model (also the fixture factories)
    ###
    @dataclass
    class Point:
        x: int
        y: int

    @dataclass
    class Circle:
        center: Point
        radius: float

    ###
    # Tests
    ###
    @fixture(Point, 0, 0, fixture_name='center')
    @fixture(Circle, radius=3, fixture_name='outer')
    @fixture(Circle, radius=2, fixture_name='inner')
    def test_case(outer, inner, **_):
        ...
    """

    kwargs = _KwargSubstitution()
    """
    fixture.kwargs['fixture_name'] can be used as a fixture_kwarg to use a
    keyword argument in the fixture stack as a different keyword argument to
    a fixture factory function. This is useful when fixture factories take
    arguments created by other fixtures when the names of the fixture and
    argument don't match. For example:
        @fixture(factory1, fixture_name='foo')
        @fixture(factory2, bar=fixture.kwargs['foo'])
        ...
    The first @fixture will create a fixture in the keyword args named foo. The
    second @fixture will call factory2 with a keyword argument bar with a value
    that is the fixture named foo created by the first @fixture.
    """

    def __init__(  # type: ignore[no-untyped-def]
        self,
        factory,
        *fixture_args,
        fixture_name=None,
        **fixture_kwargs,
    ):
        self.factory = factory
        self.fixture_args = fixture_args
        self.fixture_name = fixture_name or get_default_fixture_name(factory)
        self.fixture_kwargs = fixture_kwargs

    def __call__(self, func):  # type: ignore[no-untyped-def]
        @wraps(func)
        def wrapper(*args, **kwargs):  # type: ignore[no-untyped-def]
            substituted_fixture_kwargs = _KwargSubstitution._substitute_kwargs(
                self.fixture_kwargs, kwargs
            )

            # The factory is not passed args because those are the args to the
            # function (ie (self,)) and aren't intended for the fixture.
            # However, kwargs are provided as they will contain the fixtures
            # that should be available to the fixture function so fixtures
            # can be stacked.
            _fixture = self.factory(
                *self.fixture_args,
                **kwargs,
                **substituted_fixture_kwargs,
            )

            kwargs[self.fixture_name] = _fixture
            return func(*args, **kwargs)

        return wrapper
