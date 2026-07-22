# Python type annotations do not allow specifying that a decorator adds keyword
# arguments when calling a wrapped function. Unfortunately, this is exactly how
# @ kwargs[ works. It is untyped because there is no way to properly type it.
# Disable mypy errors that are caused by this inability to properly type it.
"""
The test cases are very abstract and concise and do not do a good job at
illustrating "real-world" use. This test module contains a contrived domain
model to illustrate how fixtures can be used in a way that should make more
sense to readers.
"""

import unittest
import pydantic
import dataclasses
import typing

from fixtures import kwargs

config = pydantic.ConfigDict(extra="allow")

_LIST_FIELD = dataclasses.field(default_factory=list[typing.Any])


###
# The data model classes. These are data classes, but since fixture factory
# methods (the dataclass.__init__) need to accept the stacked fixtures pydantic
# dataclasses configured to allow extra arguments are used. They do not need
# to be pydantic dataclasses, or event dataclasses, but it is a convenient way
# to define the model elements. See below for fixture factories that are
# functions.
###
@pydantic.dataclasses.dataclass(config=config)
class _Named:
    """Base class for model elements with a name."""

    name: str
    """the name of the entity"""


@pydantic.dataclasses.dataclass(config=config)
class Employee(_Named):
    """a company employee"""

    title: str
    """the employees title"""

    department: Department | None = None
    """the department the employee works in"""

    def __post_init__(self) -> None:
        if self.department:
            self.department.employees.append(self)


@pydantic.dataclasses.dataclass(config=config)
class Department(_Named):
    """a company department"""

    manager: Employee
    """the employee who manages this department"""

    employees: list["Employee"] = _LIST_FIELD
    """the employees that belong to this department"""

    def __post_init__(self) -> None:
        self.manager.department = self
        self.employees.append(self.manager)


@pydantic.dataclasses.dataclass(config=config)
class Company(_Named):
    """a company"""

    ceo: Employee
    """the chief executive officer of the company"""

    departments: list[Department] = _LIST_FIELD
    """the departments that make up the company"""


_Employee = kwargs.factory(Employee)
_Company = kwargs.factory(Company)
_Department = kwargs.factory(Department)


class ExampleTest(unittest.TestCase):
    @ kwargs["ceo"] << _Employee("Chuck E Oliphant", "CEO")
    def test_single_employee(self, ceo: Employee) -> None:
        assert ceo.name == "Chuck E Oliphant"

    @ kwargs["ceo"] << _Employee("Chuck E Oliphant", "CEO")
    @ kwargs["company"] << _Company("Acme Co")
    @ kwargs["alice"] << _Employee("Alice C Conte", "Accounting Manager")
    @ kwargs["accounting"] << _Department(
        "Accounting", manager=kwargs["alice"]
    )
    @ kwargs["bob"] << _Employee(
        "Bob C Paine", "Accountant", department=kwargs["accounting"]
    )
    def test_company(
        self,
        company: Company,
        ceo: Employee,
        accounting: Department,
        alice: Employee,
        bob: Employee,
        **_: typing.Any,
    ) -> None:
        assert ceo == company.ceo
        assert [] == company.departments
        assert alice == accounting.manager
        assert alice in accounting.employees
        assert alice.department == accounting
        assert bob in accounting.employees
        assert accounting == bob.department


if __name__ == "__main__":
    unittest.main()
