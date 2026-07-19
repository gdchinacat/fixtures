import unittest

from fixtures import kwargs


class KwargTest(unittest.TestCase):

    def test_kwarg_subscript(self) -> None:

        _kwarg = kwargs["kwarg"]
        self.assertEqual("kwarg", _kwarg.kwarg)

    def test_kwarg_call_fails(self) -> None:
        """
        Test using bare kwarg as decorator fails as there is no value to
        inject.
        """
        with self.assertRaises(TypeError) as te:

            @kwargs["value"]
            def func[T](value: T) -> None:
                assert False, "should never be called"

        print(str(te.exception))
        self.assertIn("<<", str(te.exception))

    def test_complete_kwarg_can_decorate(self) -> None:
        """
        Test that a complete kwarg (ie '@kwarg[...] << ...') is a decorator,
        but doesn't test it works correctly.
        """

        @ kwargs["value"] << 1
        def func(value: int):
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


if __name__ == "__main__":
    unittest.main()
