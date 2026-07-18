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


def default_fixture_name[**P, R](name: str) -> Callable[[Factory[P, R]], Factory[P, R]]:
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
    return getattr(factory, _DEFAULT_FIXTURE_NAME_ATTR, factory.__name__.lower())


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


def fixture[**P, R](
    factory: Factory[P, R],
    *fixture_args: object,
    fixture_name: str | None = None,
    **fixture_kwargs: object,
) -> Callable[[Function[P, R]], Function[P, R]]:

    def decorator(func: Function[P, R]) -> Function[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            substituted_fixture_kwargs = _KwargSubstitution._substitute_kwargs(
                fixture_kwargs, kwargs
            )

            # The factory is not passed args because those are the args to the
            # function (ie (self,)) and aren't intended for the fixture.
            # However, kwargs are provided as they will contain the fixtures
            # that should be available to the fixture function so fixtures
            # can be stacked.
            _fixture = factory(
                *fixture_args,  # type: ignore[arg-type]
                **kwargs,
                **substituted_fixture_kwargs,  # type: ignore[arg-type]
            )

            name = fixture_name or get_default_fixture_name(factory)
            kwargs[name] = _fixture
            return func(*args, **kwargs)

        return wrapper

    return decorator


fixture.kwargs = _KwargSubstitution()  # type: ignore[attr-defined]
