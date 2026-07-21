# mypy: disable-error-code=arg-type
# mypy: disable-error-code=call-arg

import unittest
from typing import Any, assert_type

from fixtures import kwargs
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


class KwargTest(unittest.TestCase):

    def test_kwarg_subscription(self) -> None:

        _kwarg = kwargs["kwarg"]
        self.assertEqual("kwarg", _kwarg.name)

    def test_kwarg_call_fails(self) -> None:
        """
        Test using bare kwarg as decorator fails as there is no value to
        inject.
        """
        with self.assertRaises(TypeError) as te:

            @kwargs["value"]
            def func[T](value: Any) -> None:
                assert False, "should never be called"

        print(str(te.exception))
        self.assertIn("<<", str(te.exception))

    def test_complete_kwarg_can_decorate(self) -> None:
        """
        Test that a complete kwarg (ie '@kwarg[...] << ...') is a decorator,
        but doesn't test it works correctly.
        """

        @ kwargs["value"] << 1
        def func(value: int) -> int:
            return value

    def test_kwarg_decorator_injects_value(self) -> None:
        """
        Test that a callable decorated with a complete kwarg has a non-factory
        value injected when called.
        """

        @ kwargs["value"] << 1
        def func(value: int) -> int:
            return value

        self.assertEqual(1, func())

    def test_kwarg_decorator_injects_factory_generated_value(self) -> None:
        """
        Test that a callable decorated with a complete kwarg has a factory
        value injected when called.
        """

        @kwargs.factory
        def factory(value: int) -> int:
            return value

        @ kwargs["value"] << factory(1)
        def func(value: int) -> int:
            return value

        self.assertEqual(1, func())

    def test_factory_kwarg_replacement_no_factory(self) -> None:
        @kwargs.factory
        def factory(value: int) -> int:
            return value

        @ kwargs["foo"] << factory(1)
        @ kwargs["value"] << kwargs["foo"]
        def func(value: int, **_: Any) -> int:
            return value

        self.assertEqual(1, func())

    def test_factory_kwarg_replacement_factory(self) -> None:
        @kwargs.factory
        def factory(value: int, **_: Any) -> int:
            return value

        @ kwargs["foo"] << factory(1)
        @ kwargs["value"] << factory(value=kwargs["foo"])
        def func(value: int, **_: Any) -> int:
            return value

        self.assertEqual(1, func())


@kwargs.factory
@dataclass(config=ConfigDict(extra="allow"))
class Data:
    a: int
    b: str


class PartialFactoryTest(unittest.TestCase):
    def test_factories_partials_with_kwargs(self) -> None:
        @ kwargs["b"] << "b"
        @ kwargs["data"] << Data(a=1)
        def foo(data: Data, **_: Any) -> Data:
            return data

        data = foo()
        self.assertEqual((1, "b"), (data.a, data.b))

    def test_factories_partials_with_args(self) -> None:
        @ kwargs["b"] << "b"
        @ kwargs["data"] << Data(1)
        def foo(data: Data, **_: Any) -> Data:
            return data

        data = foo()
        self.assertEqual((1, "b"), (data.a, data.b))

    def test_factories_get_kwargs(self) -> None:
        @ kwargs["a"] << 1
        @ kwargs["b"] << "b"
        @ kwargs["data"] << Data()
        def foo(data: Data, **_: Any) -> Data:
            return data

        data = foo()
        self.assertEqual((1, "b"), (data.a, data.b))


class DecoratorTypeTest(unittest.TestCase):
    """
    Test the type annotations for decorated functions that are inferred by type
    checkers are correct.
    """

    def test_literal(self) -> None:
        @ kwargs["_"] << ""
        def foo(**_: Any) -> int:
            return 1

        _foo = foo()
        self.assertEqual(1, _foo)
        assert_type(_foo, int)

    def test_kwarg(self) -> None:
        @ kwargs["s"] << ""
        @ kwargs["s2"] << kwargs["s"]
        def foo(**_: Any) -> int:
            return 1

        _foo = foo()
        self.assertEqual(1, _foo)
        assert_type(_foo, int)

    def test_factory(self) -> None:
        @kwargs.factory
        def factory() -> str:
            return ""

        @ kwargs["_"] << factory()
        def foo(**_: Any) -> int:
            return 1

        _foo = foo()
        self.assertEqual(1, _foo)

        assert_type(_foo, int)


if __name__ == "__main__":
    unittest.main()
