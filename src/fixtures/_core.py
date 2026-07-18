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

    Fall back to the factory __name__ if no explicit name was provided.
    """
    return getattr(factory, _DEFAULT_FIXTURE_NAME_ATTR, factory.__name__)


def fixture[**P, R](
    factory: Factory[P, R],
    fixture_name: str | None = None,
) -> Callable[[Function[P, R]], Function[P, R]]:

    def decorator(func: Function[P, R]) -> Function[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            resource = factory(*args, **kwargs)
            name = fixture_name or get_default_fixture_name(factory)
            kwargs[name] = resource
            return func(*args, **kwargs)

        return wrapper

    return decorator
