"""
TODO - fixtures elevator pitch
TODO - examples

@kwargs['foo'] << Foo(1)
@kwargs['bar'] << Bar(kwargs['foo'])
def test_foo_bar(foo: Foo, bar: Bar):
"""

from . import _kwarg
from ._kwarg import *

__all__ = () + _kwarg.__all__

del _kwarg
