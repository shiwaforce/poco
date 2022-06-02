import poco.poco as poco
from .abstract_test import AbstractTestSuite


class VersionsTestSuite(AbstractTestSuite):

    def test_version(self):
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("--version")
            self.assertIsNotNone(context.exception)
        self.assertIn(poco.__version__, out.getvalue().strip())

    def test_version_update_to_beta_tester(self):
        extra_config = dict()
        extra_config['beta_tester'] = 'True'
        self.init_poco_config(extra_config)

        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("--version")
            self.assertIsNotNone(context.exception)
        self.assertIn(poco.__version__, out.getvalue().strip())
