"""
Fixtures provides a way to decorate functions (primarily test functions) with
calls to factory methods thaat produce the fixtures the tests needs.

@fixture(class, 'calculus')
@fixture(teacher, 'Alice')
@fixture(student, 'Bob')
@fixture(student, 'Claire')
def test_cannot_enroll_student_twice(classroom, teacher, **kwargs):
     ....

This will create a class with a teacher and two students. The created fixtures
will be passed through the fixture stack and to the decorated function as
keyword arguments.
"""

from . import _core
from ._core import *

__all__ = _core.__all__
