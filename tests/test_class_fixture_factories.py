"""
Test that classes can be used as fixture factories.

TODO - this actually works, but has some pretty significant typing issues:
    1) when @kwargs.factory is used as a class decorator the type is evaluated
       as a _PartialFactory and can not be used as a type in type hints.
    2) when a @kwargs.factory decorated class is used as a fixture decorator
       RHS it expects the class initializer types, but a common case is to pass
       _Kwarg references and all are optional even if they aren't when the
       class is actually realized during the fixture decorated function call.

    The fundamental problem is that the @kwargs.factory decorated class needs
    to behave like two things depending on context. It needs to be a type as
    well as a partial class callable.

    I am not sure what the proper solution is, and can't get bogged down by
    sorting it out at the moment. So, for posterities sake (and not saying
    'go look at my other repository that may change'), here is the problem as
    a simplified test case.
"""

from dataclasses import dataclass

from fixtures import kwargs


@kwargs.factory
@dataclass
class Foo:
    attr1: int


@kwargs.factory
@dataclass
class Bar:
    foo: Foo  # type: ignore # 1: (pyright) 'error: Expected class but received "factory[(), Foo]" (reportGeneralTypeIssues)'


@ kwargs["foo"] << Foo(1)  # type: ignore # 2: (mypy) 'Missing positional argument "attr1" in call to "Foo"  [call-arg]'
@ kwargs["bar"] << Bar()  # type: ignore # 2: (mypy) 'Missing positional argument "foo" in call to "Bar"  [call-arg]'
def test_foo_bar(
    foo: Foo,  # type: ignore # 1: (pyright) 'error: Expected class but received "factory[(), Foo]" (reportGeneralTypeIssues)'
    bar: Bar,  # type: ignore # 1: (pyright) 'error: Expected class but received "factory[(), Bar]" (reportGeneralTypeIssues)'
    **_: object,
) -> None:
    assert bar.foo is foo
