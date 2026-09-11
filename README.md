Unit test helper library to help with injecting arbitrary fixtures into kwargs.

For example:
```
    @ kwargs["origin"] << _Point(0, 0)
    @ kwargs["outer"] << _Circle(3, center=kwargs["origin"])
    @ kwargs["inner"] << _Circle(2, center=kwargs["origin"])
    @ kwargs["disjoint"] << _Circle(5, center=Point(10, 10))
    def test_circle_overlap(
        self, outer: Circle, inner: Circle, disjoint: Circle, **_: Any
    ) -> None:
        ...
```

TODO:
	- pytest finds bare test functions, sees that they take arguments, and tries to find its own fixtures to satisfy them since it doesn't know the decorator chain injects them. If the test is implemented as a unittest.TestCase method pytest is able to run them properly.
