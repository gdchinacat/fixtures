"""
Test interactions with pytest.
"""

from typing import Any

import pytest

from fixtures import kwargs


class PytestFixture: ...


class KwargFixture: ...


@pytest.fixture
def pytest_fixture() -> PytestFixture:
    return PytestFixture()


@kwargs.factory
def kwarg_fixture(**_: Any) -> KwargFixture:
    return KwargFixture()


@ kwargs["kwarg_fixture"] << kwarg_fixture()
def test_pytest_and_kwargs(
    pytest_fixture: PytestFixture, kwarg_fixture: KwargFixture | None = None
) -> None:
    assert isinstance(pytest_fixture, PytestFixture)
    assert isinstance(kwarg_fixture, KwargFixture)
