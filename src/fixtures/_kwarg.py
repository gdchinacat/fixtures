from typing import Any, Callable
from dataclasses import dataclass

__all__ = ("kwargs",)


type Factory = Callable[..., Any] | object
"""
Factory is the type that creates keyword argument values when decorated
functions are called.
"""


@dataclass
class _Factory:
    partial: _Partial
    args: tuple[object, ...]
    kwargs: dict[str, object]

    def __call__(self, *args: object, **kwargs: object):
        return self.partial.factory(*self.args, *args, **self.kwargs, **kwargs)


@dataclass
class _Partial:
    factory: _Factory

    def __call__(self, *args: object, **kwargs: object) -> _Factory:
        return _Factory(self, args, kwargs)


@dataclass
class _KwargFactoryDecorator:  # todo name doesn't seem right
    """
    Decorator that wraps a callable that creates and injects a kwarg into the
    kwargs the callable is called with.
    """

    kwarg: Kwarg
    value: Factory

    def __call__(self, func):
        def dec(*args, **kwargs):
            # todo - actually create the kwarg value
            value = (
                self.value(*args, **kwargs)
                if isinstance(self.value, _Factory)
                else self.value
            )
            kwargs[self.kwarg.kwarg] = value
            return func(*args, **kwargs)

        return dec


class _PartialDecorator[**P, R]:
    """
    Decorator (class or callable) to create a _Partial that can be used with
    a _Kwarg reference to create a _KwargFactoryDecorator.
    """

    def __init__(self, factory: Factory) -> None:
        """
        decorate the factory so that when called it remembers the provided
        *args, **kwags so that when called they are mixed with the call args
        and kwargs to create the actual kwarg.
        """


@dataclass
class Kwarg:
    """
    _Kwarg is a reference to a kwarg.
    It is basically a name with a bit of functionality:
        - marker to replace a kwarg with another kwarg when executing the
          decorator stack.
        - functionality to create a decorator that will inject a kwarg:
          _Kwarg(...) << ...

    Pipe dream: if __setitem__() was allowed to return a value, and the
    'cannot assign to subscript here' error was removed when trying to assign
    a subscript in a decorator, this class could implement __setitem__() rather
    than __lshift__() and the decorator could be spelled '@ kwarg['foo'] = 1'.
    """

    kwarg: str
    """the name of the kwarg"""

    def __call__(self, *args: Any, **kwargs: Any) -> None:
        raise TypeError(
            "incomplete Kwarg can not be used as decorator, "
            "complete it by providing a value using "
            "'@kwarg['kwarg'] << ...'"
        )

    def __lshift__(self, factory: Factory) -> _KwargFactoryDecorator:
        return _KwargFactoryDecorator(self, factory)


class _KwargFactory:
    factory = _Partial

    def __class_getitem__(self, kwarg: str) -> Kwarg:
        return Kwarg(kwarg)  # todo? - intern this?


kwargs = _KwargFactory
