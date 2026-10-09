"""
Test interactions with pytest.
"""

from typing import Any

import pytest

from fixtures import kwargs


class PytestFixture: ...


class KwargFixture: ...


pytest_dummy = pytest.fixture(lambda: None)


@pytest.fixture
def pytest_fixture() -> PytestFixture:
    return PytestFixture()


def _kwarg_fixture(**_: Any) -> KwargFixture:
    return KwargFixture()


kwarg_factory = kwargs.factory(_kwarg_fixture)
kwarg_fixture = pytest_dummy


@ kwargs["kwarg_fixture"] << kwarg_factory()
def test_pytest_and_kwargs(
    pytest_fixture: PytestFixture, kwarg_fixture: KwargFixture
) -> None:
    assert isinstance(pytest_fixture, PytestFixture)
    assert isinstance(kwarg_fixture, KwargFixture)
