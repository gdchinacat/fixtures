"""
Test interactions with pytest.
"""

from dataclasses import dataclass
import pytest
from typing import Any

from fixtures import kwargs


class PytestFixture: ...


@dataclass
class KwargFixture:
    arg1: int
    pytest_fixture: PytestFixture | None = None


@pytest.fixture
def pytest_fixture() -> PytestFixture:
    return PytestFixture()


@kwargs.factory
def kwarg_fixture(arg1: int, **_: Any) -> KwargFixture:
    return KwargFixture(arg1)


@kwargs.factory
def kwarg_takes_pytest_fixture(
    arg1: int, pytest_fixture: PytestFixture, **_: Any
) -> KwargFixture:
    return KwargFixture(arg1, pytest_fixture)


@ kwargs["kwarg_fixture"] << kwarg_fixture(1)
def test_pytest_and_kwargs(
    pytest_fixture: PytestFixture,
    kwarg_fixture: KwargFixture,
) -> None:
    assert isinstance(pytest_fixture, PytestFixture)
    assert isinstance(kwarg_fixture, KwargFixture)


@ kwargs["kwarg_fixture"] << kwarg_takes_pytest_fixture(1)
def test_kwarg_fixture_takes_pytest_fixture(
    kwarg_fixture: KwargFixture,
    **_: Any,  # pytest_fixture is injected by pytest to satisfy kwarg_fixture
) -> None:
    assert isinstance(kwarg_fixture, KwargFixture)
    assert isinstance(kwarg_fixture.pytest_fixture, PytestFixture)
