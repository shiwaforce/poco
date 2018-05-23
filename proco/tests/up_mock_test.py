from .abstract_test import AbstractTestSuite
from proco.services.environment_utils import EnvironmentUtils

try:
    from unittest import mock
except ImportError:
    import mock


class ProcoDockerTestSuite(AbstractTestSuite):

    @mock.patch('proco.services.environment_utils.EnvironmentUtils.check_docker')
    @mock.patch('proco.services.command_runners.AbstractPlanRunner.run_script_with_check')
    def test_up_and_down_mock(self, run_script_with_check, check_docker):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_proco_command("start", "nginx")
        self.assertEqual(0, len(err.getvalue()))
        with self.captured_output() as (out, err):
            self.run_proco_command("stop", "nginx")
        self.assertEqual(0, len(err.getvalue()))

    @mock.patch('proco.services.environment_utils.EnvironmentUtils.check_docker')
    @mock.patch('proco.services.command_runners.AbstractPlanRunner.run_script_with_check')
    def test_pull_mock(self, run_script_with_check, check_docker):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_proco_command("pull", "nginx")
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("Project pull complete", out.getvalue().strip())

    @mock.patch('proco.services.environment_utils.EnvironmentUtils.check_docker')
    @mock.patch('proco.services.command_runners.AbstractPlanRunner.run_script_with_check')
    @mock.patch('proco.services.package_handler.PackageHandler.run_save_cmd')
    def test_pack_mock(self, check_docker, run_script, run_save):
        self.init_with_remote_catalog()
        with mock.patch.object(EnvironmentUtils, 'decode') as mock_method:
            mock_method.return_value = "Test Docker file."
            with self.captured_output() as (out, err):
                self.run_proco_command("pack", "nginx/default")
            self.assertEqual(0, len(err.getvalue()))
