

TODO:
	- pytest finds bare test functions, sees that they take arguments, and tries to find its own fixtures to satisfy them since it doesn't know the decorator chain injects them. If the test is implemented as a unittest.TestCase method pytest is able to run them properly.
