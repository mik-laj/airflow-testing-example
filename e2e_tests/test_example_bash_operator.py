from e2e_tests.utils import E2ETestCase


class TestExampleBashOperatorE2EDag(E2ETestCase):
    def test_should_finish_with_success(self):
        self.run_dag("example_bash_operator2")
