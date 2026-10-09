"""
Test that @kwargs.factory functions can be context managers and they are exited
properly.
"""

from collections.abc import Generator
from contextlib import contextmanager
from typing import ClassVar

import pytest

from fixtures import kwargs
from dataclasses import dataclass


@dataclass
class FixtureTrace:
    entered = False
    tested = False
    exited = False


class Fixture:
    __test__ = False
    suppress: ClassVar[bool] = False

    def __init__(self, trace: FixtureTrace):
        self.trace = trace

    @classmethod
    def assert_trace_valid(cls, trace: FixtureTrace) -> None:
        assert trace.entered and trace.tested and trace.exited

    def enter(self) -> None:
        self.trace.entered = True

    def test(self) -> None:
        self.trace.tested = True

    def exit(self) -> None:
        self.trace.exited = True


class RaisingFixture(Fixture):
    def test(self) -> None:
        super().test()
        raise Exception

    @classmethod
    def assert_trace_valid(cls, trace: FixtureTrace) -> None:
        assert trace.entered and trace.tested and trace.exited


class SuppressingFixture(RaisingFixture):
    suppress: ClassVar[bool] = True


@pytest.mark.parametrize(
    "fixture_type",
    (
        Fixture,
        RaisingFixture,
        SuppressingFixture,
    ),
)
def test_context_manager(fixture_type: type[Fixture]) -> None:

    trace = FixtureTrace()

    @kwargs.factory
    @contextmanager
    def cm_fixture(
        fixture_type: type[Fixture], trace: FixtureTrace
    ) -> Generator[Fixture]:
        fixture = fixture_type(trace)
        fixture.enter()
        ret: bool = False
        try:
            yield fixture
        except:
            if not fixture.suppress:
                raise
        finally:
            fixture.exit()

    @ kwargs["trace"] << trace
    @ kwargs["fixture"] << cm_fixture(fixture_type)
    def test(
        fixture_type: type[Fixture], trace: FixtureTrace, fixture: Fixture
    ) -> Fixture:
        fixture.test()
        return fixture

    try:
        fixture = test(fixture_type)  # type: ignore  # kwargs achiles heel
    except:
        assert not fixture_type.suppress
    finally:
        fixture_type.assert_trace_valid(trace)
