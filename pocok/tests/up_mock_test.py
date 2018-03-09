import subprocess
from .abstract_test import AbstractTestSuite
try:
    from unittest import mock
except ImportError:
    import mock


class PocokDockerTestSuite(AbstractTestSuite):

    @mock.patch('pocok.services.environment_utils.EnvironmentUtils.check_docker')
    @mock.patch('pocok.services.command_runners.AbstractPlanRunner.run_script_with_check')
    def test_up_and_down_mock(self, run_script_with_check, check_docker):
        self.init_with_remote_catalog()
        check_docker.return_value = None
        run_script_with_check.return_value = None
        with self.captured_output() as (out, err):
            self.run_pocok_command("start", "nginx")
        self.assertEqual(0, len(err.getvalue()))
        self.assertEqual(0, len(out.getvalue()))
        with self.captured_output() as (out, err):
            self.run_pocok_command("stop", "nginx")
        self.assertEqual(0, len(err.getvalue()))
        self.assertEqual(0, len(out.getvalue()))

    @mock.patch('pocok.services.environment_utils.EnvironmentUtils.check_docker')
    @mock.patch('pocok.services.command_runners.AbstractPlanRunner.run_script_with_check')
    def test_pull_mock(self, run_script_with_check, check_docker):
        self.init_with_remote_catalog()
        check_docker.return_value = None
        run_script_with_check.return_value = None
        with self.captured_output() as (out, err):
            self.run_pocok_command("pull", "nginx")
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("Project pull complete", out.getvalue().strip())
