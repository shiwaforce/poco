import poco.poco as poco
from .abstract_test import AbstractTestSuite
try:
    from unittest import mock
except ImportError:
    import mock


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

    @mock.patch('poco.poco.__version__', '0.98.10')
    @mock.patch('poco.services.environment_utils.EnvironmentUtils.parse_version')
    def test_version_compare(self, parse_version):
        parse_version.return_value = "0.100.0"

        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("--version")
            self.assertIsNotNone(context.exception)
        print(out.getvalue().strip())
        self.assertIn("0.100.0", out.getvalue().strip())
