# Python type annotations do not allow specifying that a decorator adds keyword
# arguments when calling a wrapped function. Unfortunately, this is exactly how
# @fixture works. It is untyped because there is no way to properly type it.
# Disable mypy errors that are caused by this inability to properly type it.
# mypy: disable-error-code=no-untyped-call
#     @fixture is untyped
# mypy: disable-error-code=untyped-decorator
#     Untyped decorator makes function "..." untyped  [untyped-decorator]

import pytest
from fixtures import default_fixture_name, get_default_fixture_name, fixture
from typing import Any


def test_get_default_fixture_name_unset() -> None:
    def _factory() -> None: ...

    assert "_factory" == get_default_fixture_name(_factory)


def test_default_fixture_name_set() -> None:
    @default_fixture_name("fixture")
    def _factory() -> None: ...

    assert "fixture" == get_default_fixture_name(_factory)


def test_default_fixture_name_fails_if_already_set() -> None:
    with pytest.raises(AttributeError):

        @default_fixture_name("fixture")
        @default_fixture_name("fixture")
        def _factory() -> None: ...


def test_fixture_default_name() -> None:
    _fixture = object()

    def _factory() -> object:
        return _fixture

    @fixture(_factory)
    def func(_factory: object) -> object:
        return _factory

    assert _fixture is func()


def test_fixture_decorated_func_looks_like_func() -> None:
    def _factory() -> object:
        return object()

    def _func(_fixture: object) -> object:
        """pydoc"""

    # Invoke decorator manually in order to retain reference to the original
    # function to compare with.
    func = fixture(_factory)(_func)

    assert _func.__name__ == func.__name__
    assert _func.__doc__ == func.__doc__


def test_fixture_name_used() -> None:
    _fixture = object()

    def _factory() -> object:
        return _fixture

    @fixture(_factory, fixture_name="named_fixture")
    def func(named_fixture: object) -> object:
        return named_fixture

    assert _fixture is func()


class Fixture[*TAs]:
    def __init__(self, *args: *TAs, **kwargs: object) -> None:
        self.args = args
        self.kwargs = kwargs


type NoArgFixture = Fixture[()]


def test_factory_args_kwargs() -> None:
    args = ("arg1", "arg2")
    kwargs = {"kwarg1": "kwarg1", "kwarg2": "kwarg2"}

    @fixture(Fixture[str, str], *args, **kwargs)
    def func(fixture: Fixture[str, str]) -> tuple[object, object]:
        return fixture.args, fixture.kwargs

    assert (args, kwargs) == func()


def test_fixture_decorated_method_args() -> None:
    """test that self is handled properly"""

    class TestCase:
        @fixture(Fixture, "arg1")
        def test(self, fixture: Fixture[str]) -> str:
            return fixture.args[0]

    assert "arg1" == TestCase().test()


def test_stacked_fixtures_receive_previous_fixtures() -> None:
    @fixture(Fixture, fixture_name="fixture1")
    @fixture(Fixture, fixture_name="fixture2")
    def func(fixture2: Fixture[NoArgFixture], **_: Any) -> Fixture[NoArgFixture]:
        return fixture2

    assert "fixture1" in func().kwargs


def test_factory_kwarg_substitution() -> None:
    @fixture(Fixture, fixture_name="f1")
    @fixture(Fixture, fixture=fixture.kwargs["f1"])
    def func(
        fixture: NoArgFixture, f1: NoArgFixture
    ) -> tuple[NoArgFixture, NoArgFixture]:
        return (fixture, f1)

    _fixture, f1 = func()
    assert {"fixture": f1, "f1": f1} == _fixture.kwargs
