from unittest import TestCase, skip

class TestApps(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_loader(self):
        pass

@skip('todo:')
class TestModules(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_loader(self):
        pass

