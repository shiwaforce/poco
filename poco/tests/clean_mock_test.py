import subprocess
from .abstract_test import AbstractTestSuite
try:
    from unittest import mock
except ImportError:
    import mock


class PocoTestSuite(AbstractTestSuite):

    @mock.patch('poco.services.environment_utils.EnvironmentUtils.check_docker')
    def test_clean(self, check_docker):
        check_docker.return_value = None
        with mock.patch('subprocess.check_output') as mock_check_output:
            mock_check_output.call = mock.create_autospec(subprocess.call, return_value='mocked!')
            with self.captured_output() as (out, err):
                self.run_poco_command("clean")
            self.assertEqual(0, len(err.getvalue()))
