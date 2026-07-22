# Python type annotations do not allow specifying that a decorator adds keyword
# arguments when calling a wrapped function. Unfortunately, this is exactly how
# @fixture works. It is untyped because there is no way to properly type it.
# Disable mypy errors that are caused by this inability to properly type it.

import pytest
from fixtures import kwargs
from typing import Any


def test_fixture_decorated_func_looks_like_func() -> None:
    def _factory() -> object:
        return object()

    def _func(_fixture: object) -> object:
        """pydoc"""

    # Invoke decorator manually in order to retain reference to the original
    # function to compare with.
    func = (kwargs["_factory"] << _factory)(_func)

    assert _func.__name__ == func.__name__
    assert _func.__doc__ == func.__doc__


@kwargs.factory
class Fixture:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs


def test_factory_args_kwargs() -> None:
    _args = ("arg1", "arg2")
    _kwargs = {"kwarg1": "kwarg1", "kwarg2": "kwarg2"}

    @ kwargs["fixture"] << Fixture(*_args, **_kwargs)
    def func(fixture: Fixture) -> tuple[object, object]:
        return fixture.args, fixture.kwargs

    assert (_args, _kwargs) == func()  # type: ignore[call-arg]


def test_fixture_decorated_method_args() -> None:
    """test that self is handled properly"""

    class TestCase:
        @ kwargs["fixture"] << Fixture("arg1")
        def test(self, fixture: Fixture) -> str:
            return fixture.args[0]  # type: ignore[no-any-return]

    assert "arg1" == TestCase().test()  # type: ignore[call-arg]


def test_stacked_fixtures_receive_previous_fixtures() -> None:
    @ kwargs["fixture1"] << Fixture()
    @ kwargs["fixture2"] << Fixture()
    def func(fixture2: Fixture, **_: Any) -> Fixture:
        return fixture2

    assert "fixture1" in func().kwargs  # type: ignore[call-arg]


def test_factory_kwarg_substitution() -> None:
    @ kwargs["f1"] << Fixture()
    @ kwargs["fixture"] << Fixture(fixture=kwargs["f1"])
    def func(f1: Fixture, fixture: Fixture) -> tuple[Fixture, Fixture]:
        return (fixture, f1)

    _fixture, f1 = func()  # type: ignore[call-arg]
    assert {"fixture": f1, "f1": f1} == _fixture.kwargs
