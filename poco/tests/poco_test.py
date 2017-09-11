import git
import os
import yaml
from docopt import DocoptExit
from .abstract_test import AbstractTestSuite
from poco.poco import Poco
from poco.services.state import StateHolder


class ComposeTestSuite(AbstractTestSuite):

    def test_without_command(self):
        with self.assertRaises(DocoptExit) as context:
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=[""])
            poco.run()
        self.assertIsNotNone(context.exception)

    def test_wrong_parameters(self):
        with self.assertRaises(DocoptExit) as context:
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["notexistcommand"])
            poco.run()
        self.assertIsNotNone(context.exception)

    def test_config_without_config(self):
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "config"])
            poco.run()
        self.assertEqual(0, len(err.getvalue()))
        AbstractTestSuite.REMOTE_CONFIG.pop('workspace')
        self.assertIn(yaml.dump(data=AbstractTestSuite.REMOTE_CONFIG, default_flow_style=False, default_style='',
                                indent=4).strip(), out.getvalue().strip())

    def test_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "config"])
            poco.run()
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn(yaml.dump(data=AbstractTestSuite.REMOTE_CONFIG, default_flow_style=False, default_style='',
                                indent=4).strip(), out.getvalue().strip())

    def test_list_with_local_config(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "ls"])
            poco.run()
        self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())

    def test_list_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "ls"])
            poco.run()
        self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())

    def test_branches_with_local_config(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "branches"])
            poco.run()
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn('Available branches in', out.getvalue().strip())
        self.assertNotIn('master', out.getvalue().strip())

    def test_branches_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "branches"])
            poco.run()
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn('Available branches in', out.getvalue().strip())
        self.assertIn('master', out.getvalue().strip())

    def test_switch_branch_with_local_config(self):
        self.init_with_local_catalog()
        with self.assertRaises(SystemExit) as context:
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "branch", "master"])
            poco.run()
        self.assertEqual(1, context.exception.code)

    def test_switch_branch_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "branch", "master"])
            poco.run()
        self.assertIn("Branch changed", out.getvalue())

    def test_push_with_local_config(self):
        self.init_with_local_catalog()
        StateHolder.skip_docker = True
        poco = Poco(home_dir=self.tmpdir, argv=["catalog", "push"])
        with self.captured_output() as (out, err):
            poco.run()
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn("Push completed", out.getvalue())

    def test_add_and_remove(self):
        self.init_with_local_catalog()
        test_dir = os.path.join(self.tmpdir, "test-directory")
        os.makedirs(test_dir)
        git.Repo.clone_from(url=AbstractTestSuite.STACK_LIST_SAMPLE['nginx']['git'], to_path=test_dir)
        StateHolder.skip_docker = True
        poco = Poco(home_dir=self.tmpdir, argv=["catalog", "add", test_dir])
        with self.captured_output() as (out, err):
            poco.run()
        self.assertIn("Project added", out.getvalue())
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "ls"])
            poco.run()
            self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())
        self.assertIn("test-directory", out.getvalue())
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "remove", "test-directory"])
            poco.run()
        self.assertIn("Project removed", out.getvalue())
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "ls"])
            poco.run()
            self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())
        self.assertNotIn("test-directory", out.getvalue())

    def test_plan_list(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["plan", "ls", "mysql"])
            poco.run()
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("default", out.getvalue())

    def test_branches(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["branches", "mysql"])
            poco.run()
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("master", out.getvalue())

    def test_branch_without_change_branch(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["branch", "mysql", "master"])
            poco.run()
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("Branch changed", out.getvalue())

    def test_init(self):
        self.init_with_local_catalog()
        test_dir = os.path.join(self.tmpdir, "test-directory")
        os.makedirs(test_dir)
        git.Repo.clone_from(url=AbstractTestSuite.STACK_LIST_SAMPLE['nginx']['git'], to_path=test_dir)
        StateHolder.skip_docker = True
        poco = Poco(home_dir=self.tmpdir, argv=["catalog", "add", test_dir])
        with self.captured_output() as (out, err):
            poco.run()
        self.assertIn("Project added", out.getvalue())
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["catalog", "ls"])
            poco.run()
            self.assertEqual(0, len(err.getvalue().strip()))
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["init", "test-directory"])
            poco.run()
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("Project init completed", out.getvalue())
        self.assertTrue(os.path.exists(self.ws_dir))
        self.assertTrue(os.path.exists(os.path.join(self.ws_dir, "test-directory")))
        self.assertTrue(os.path.exists(os.path.join(self.ws_dir, "test-directory/poco.yml")))
        self.assertTrue(os.path.exists(os.path.join(self.ws_dir, "test-directory/docker-compose.yml")))

    def test_install(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            StateHolder.skip_docker = True
            poco = Poco(home_dir=self.tmpdir, argv=["install", "mysql"])
            poco.run()
        self.assertEqual(0, len(err.getvalue()))
        self.assertTrue(os.path.exists(self.ws_dir))
        self.assertTrue(os.path.exists(os.path.join(self.ws_dir, "poco-example")))
