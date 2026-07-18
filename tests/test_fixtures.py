import pytest
from fixtures import default_fixture_name, get_default_fixture_name, fixture


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
