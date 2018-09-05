import git
import os
import yaml
import poco.poco as poco
from .abstract_test import AbstractTestSuite
from poco.services.file_utils import FileUtils
from poco.services.cta_utils import CTAUtils


class PocoTestSuite(AbstractTestSuite):

    def test_without_command(self):
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command()
            self.assertIsNotNone(context.exception)
        self.assertIn(poco.__doc__.strip(), out.getvalue().strip())
        self.assertIn(poco.END_STRING.strip(), out.getvalue().strip())

    def test_version(self):
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("--version")
            self.assertIsNotNone(context.exception)
        self.assertIn(poco.__version__, out.getvalue().strip())

    def test_help_command(self):
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("help")
            self.assertIsNotNone(context.exception)
        self.assertIn(poco.__doc__.strip(), out.getvalue().strip())
        self.assertIn(CTAUtils.CTA_STRINGS['default'], out.getvalue())

    def test_help_command_with_catalog(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("help")
            self.assertIsNotNone(context.exception)
        self.assertIn(poco.__doc__.strip(), out.getvalue().strip())
        self.assertIn(CTAUtils.CTA_STRINGS['have_cat'], out.getvalue())

    def test_help_command_with_poco_file(self):
        self.init_empty_compose_file()
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("help")
            self.assertIsNotNone(context.exception)
        self.assertIn(poco.__doc__.strip(), out.getvalue().strip())
        self.assertIn(CTAUtils.CTA_STRINGS['have_file'], out.getvalue())

    def test_help_command_with_everything(self):
        self.init_empty_compose_file()
        self.init_poco_file()
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("help")
            self.assertIsNotNone(context.exception)
        self.assertIn(poco.__doc__.strip(), out.getvalue().strip())
        self.assertIn(CTAUtils.CTA_STRINGS['have_all'], out.getvalue())

    def test_subcommand_help(self):
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("repo")
            self.assertIsNotNone(context.exception)
        output = out.getvalue().strip()
        self.assertIn("Poco repo commands\n", output)
        self.assertIn("Usage:", output)

    def test_wrong_parameters(self):
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("notexistcommand")
            self.assertIsNotNone(context.exception)
        self.assertIn("is not a poco command. See 'poco help'.", out.getvalue().strip())

    def test_config_without_config(self):
        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "ls")
        self.assertIn("Actual config\n-------------\n", out.getvalue().strip())

    def test_config_with_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "ls")
        out_string = out.getvalue().strip()
        self.assertIn("Actual config\n-------------\n", out_string)
        self.assertIn("Mode: developer\nOffline: False\nAlways update: False", out_string)
        self.assertIn("Working directory: " + str(self.ws_dir), out_string)
        self.assertIn("Config location: " + str(self.config_file), out_string)
        self.assertIn(yaml.dump(AbstractTestSuite.REMOTE_CONFIG, default_flow_style=False, default_style='', indent=4)
                      .strip(), out_string)

    def test_config_with_config_and_demo_mode(self):
        extra_config = dict()
        extra_config['mode'] = 'demo'
        self.init_with_remote_catalog(extra_config)
        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "ls")
        out_string = out.getvalue().strip()
        self.assertIn("Actual config\n-------------\n", out_string)
        self.assertIn("Mode: demo\nOffline: False\nAlways update: True", out_string)
        self.assertIn("Working directory: " + str(self.ws_dir), out_string)
        self.assertIn("Config location: " + str(self.config_file), out_string)
        self.assertIn(yaml.dump(AbstractTestSuite.REMOTE_CONFIG, default_flow_style=False, default_style='', indent=4)
                      .strip(), out_string)

    def test_config_with_config_and_server_mode(self):
        extra_config = dict()
        extra_config['mode'] = 'server'
        self.init_with_remote_catalog(extra_config)
        os.mkdir(os.path.join(self.tmpdir, 'catalogHome'))
        os.mkdir(os.path.join(self.tmpdir, 'catalogHome', 'default'))
        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "ls")
        out_string = out.getvalue().strip()
        self.assertIn("Actual config\n-------------\n", out_string)
        self.assertIn("Mode: server\nOffline: True\nAlways update: False", out_string)
        self.assertIn("Working directory: " + str(self.ws_dir), out_string)
        self.assertIn("Config location: " + str(self.config_file), out_string)
        self.assertIn(yaml.dump(AbstractTestSuite.REMOTE_CONFIG, default_flow_style=False, default_style='', indent=4)
                      .strip(), out_string)

    def test_config_with_config_and_options(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("--offline", "--always-update", "repo", "ls")
        out_string = out.getvalue().strip()
        self.assertIn("Actual config\n-------------\n", out_string)
        self.assertIn("Mode: developer\nOffline: True\nAlways update: True", out_string)
        self.assertIn("Working directory: " + str(self.ws_dir), out_string)
        self.assertIn("Config location: " + str(self.config_file), out_string)
        self.assertIn(yaml.dump(AbstractTestSuite.LOCAL_CONFIG, default_flow_style=False, default_style='', indent=4)
                      .strip(), out_string)

    def test_catalog_without_catalog(self):
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("catalog")
            self.assertIsNotNone(context.exception)
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn(CTAUtils.CTA_STRINGS['default'], out.getvalue().strip())
        self.assertIn("You have not catalog yet.", out.getvalue().strip())

    def test_catalog_with_empty_catalog(self):
        with open(self.config_file, 'w+') as stream:
            data = dict()
            data['default'] = dict()
            yaml.dump(data=data, stream=stream, default_flow_style=False, default_style='', indent=4)
        with self.captured_output() as (out, err):
            self.run_poco_command("catalog")
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("Project catalog is empty. You can add projects with 'poco repo add' command",
                      out.getvalue().strip())

    def test_catalog(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("catalog")
        self.assertEqual(0, len(err.getvalue()))
        catalog = out.getvalue().strip()
        self.assertIn("Available projects:", catalog)
        with self.captured_output() as (out, err):
            self.run_poco_command("project", "ls")
        self.assertEqual(0, len(err.getvalue()))
        self.assertEqual(catalog, out.getvalue().strip())

    def test_catalog_with_param_that_not_exists(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("catalog", "asd")
            self.assertIsNotNone(context.exception)
        self.assertEqual(0, len(err.getvalue()))
        catalog = out.getvalue().strip()
        self.assertNotIn("Available projects:", catalog)
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("project", "ls", "asd")
            self.assertIsNotNone(context.exception)
        self.assertEqual(0, len(err.getvalue()))
        self.assertEqual(catalog, out.getvalue().strip())

    def test_catalog_with_param(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("catalog", "default")
        self.assertEqual(0, len(err.getvalue()))
        catalog = out.getvalue().strip()
        self.assertIn("Available projects:", catalog)
        with self.captured_output() as (out, err):
            self.run_poco_command("project", "ls")
        self.assertEqual(0, len(err.getvalue()))
        self.assertEqual(catalog, out.getvalue().strip())

    def test_add_modify_and_remove_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "add", "test", "https://github.com/shiwaforce/poco-example",
                                   "master", "poco-catalog.yaml")
        self.assertEqual(0, len(err.getvalue()))
        data = dict()
        data["test"] = dict()
        data["test"]["branch"] = "master"
        data["test"]["file"] = "poco-catalog.yaml"
        data["test"]["repositoryType"] = "git"
        data["test"]["server"] = "https://github.com/shiwaforce/poco-example"

        self.assertIn(yaml.dump(data, default_flow_style=False, default_style='', indent=4).strip(),
                      out.getvalue().strip())
        self.clean_states()

        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "modify", "test", "https://github.com/shiwaforce/procok.git",
                                   "master", "test2.yml")

        data["test"]["branch"] = "master"
        data["test"]["file"] = "test2.yml"
        data["test"]["server"] = "https://github.com/shiwaforce/procok.git"

        self.assertIn(yaml.dump(data, default_flow_style=False, default_style='', indent=4).strip(),
                      out.getvalue().strip())
        self.clean_states()

        with self.captured_output() as (out, err):
            self.run_poco_command("--offline", "repo", "remove", "test")
        self.assertEqual(0, len(err.getvalue()))
        self.assertNotIn("test", out.getvalue().strip())

    def test_add_modify_and_remove_config_github(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("github", "add", "test", "thisistoken", "http://test/test")
        self.assertEqual(0, len(err.getvalue()))
        data = dict()
        data["test"] = dict()
        data["test"]["token"] = "thisistoken"
        data["test"]["repositoryType"] = "github"
        data["test"]["server"] = "http://test/test"

        self.assertIn(yaml.dump(data, default_flow_style=False, default_style='', indent=4).strip(),
                      out.getvalue().strip())
        self.clean_states()

        with self.captured_output() as (out, err):
            self.run_poco_command("github", "modify", "test", "user/pass")

        data = dict()
        data["test"] = dict()
        data["test"]["user"] = "user"
        data["test"]["pass"] = "pass"
        data["test"]["repositoryType"] = "github"

        self.assertIn(yaml.dump(data, default_flow_style=False, default_style='', indent=4).strip(),
                      out.getvalue().strip())
        self.clean_states()

        with self.captured_output() as (out, err):
            self.run_poco_command("--offline", "repo", "remove", "test")
        self.assertEqual(0, len(err.getvalue()))
        self.assertNotIn("test", out.getvalue().strip())

    def test_add_modify_and_remove_config_gitlab(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("gitlab", "add", "test", "xxxxxx",
                                   "http://test/test", "/ssh/ssh2")
        self.assertEqual(0, len(err.getvalue()))
        data = dict()
        data["test"] = dict()
        data["test"]["token"] = "xxxxxx"
        data["test"]["repositoryType"] = "gitlab"
        data["test"]["server"] = "http://test/test"
        data["test"]["ssh"] = "/ssh/ssh2"

        self.assertIn(yaml.dump(data, default_flow_style=False, default_style='', indent=4).strip(),
                      out.getvalue().strip())
        self.clean_states()

        with self.captured_output() as (out, err):
            self.run_poco_command("gitlab", "modify", "test", "anothertoken")

        data = dict()
        data["test"] = dict()
        data["test"]["token"] = "anothertoken"
        data["test"]["repositoryType"] = "gitlab"

        self.assertIn(yaml.dump(data, default_flow_style=False, default_style='', indent=4).strip(),
                      out.getvalue().strip())
        self.clean_states()

        with self.captured_output() as (out, err):
            self.run_poco_command("--offline", "repo", "remove", "test")
        self.assertEqual(0, len(err.getvalue()))
        self.assertNotIn("test", out.getvalue().strip())

    def test_add_modify_and_remove_config_bitbucket(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("bitbucket", "add", "test", "user/pass",
                                   "http://test/test", "/ssh/ssh2")
        self.assertEqual(0, len(err.getvalue()))
        data = dict()
        data["test"] = dict()
        data["test"]["user"] = "user"
        data["test"]["pass"] = "pass"
        data["test"]["repositoryType"] = "bitbucket"
        data["test"]["server"] = "http://test/test"
        data["test"]["ssh"] = "/ssh/ssh2"

        self.assertIn(yaml.dump(data, default_flow_style=False, default_style='', indent=4).strip(),
                      out.getvalue().strip())
        self.clean_states()

        with self.captured_output() as (out, err):
            self.run_poco_command("bitbucket", "modify", "test", "user2/pass2")

        data = dict()
        data["test"] = dict()
        data["test"]["user"] = "user2"
        data["test"]["pass"] = "pass2"
        data["test"]["repositoryType"] = "bitbucket"

        self.assertIn(yaml.dump(data, default_flow_style=False, default_style='', indent=4).strip(),
                      out.getvalue().strip())
        self.clean_states()

        with self.captured_output() as (out, err):
            self.run_poco_command("--offline", "repo", "remove", "test")
        self.assertEqual(0, len(err.getvalue()))
        self.assertNotIn("test", out.getvalue().strip())

    def test_add_if_catalog_not_exists(self):
        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "add", "test", "https://github.com/shiwaforce/poco-example",
                                   "master", "poco-catalog.yaml")
            self.assertEqual(0, len(err.getvalue()))
            data = dict()
            data["test"] = dict()
            data["test"]["branch"] = "master"
            data["test"]["file"] = "poco-catalog.yaml"
            data["test"]["repositoryType"] = "git"
            data["test"]["server"] = "https://github.com/shiwaforce/poco-example"

            self.assertIn(yaml.dump(data, default_flow_style=False, default_style='', indent=4).strip(),
                          out.getvalue().strip())

    def test_branches_with_local_config(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "branches")
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn('Branch is not supported in this repository.', out.getvalue().strip())

    def test_branches_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "branches")
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn('Available branches in', out.getvalue().strip())
        self.assertIn('master', out.getvalue().strip())

    def test_switch_branch_with_local_config(self):
        self.init_with_local_catalog()
        with self.assertRaises(SystemExit) as context:
            self.run_poco_command("repo", "branch", "master")
        self.assertEqual(1, context.exception.code)

    def test_switch_branch_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "branch", "master")
        self.assertIn("Branch changed", out.getvalue())

    def test_push_with_local_config(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("repo", "push")
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn("Push completed", out.getvalue())

    def test_failed_add(self):
        self.init_with_local_catalog()
        test_dir = os.path.join(self.tmpdir, "test-directory")
        os.makedirs(test_dir)
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("project", "add", test_dir)
            self.assertIsNotNone(context.exception)
        self.assertIn("Target directory or parents are not a valid git repository", out.getvalue().strip())

    def test_failed_add_without_poco_file(self):
        self.init_with_local_catalog()
        test_dir = os.path.join(self.tmpdir, "test-directory")
        os.makedirs(test_dir)
        git.Repo.clone_from(url=AbstractTestSuite.STACK_LIST_SAMPLE['nginx']['git'], to_path=test_dir)
        os.remove(os.path.join(test_dir, 'nginx', 'poco.yml'))
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("project", "add", test_dir)
            self.assertIsNotNone(context.exception)
        self.assertIn("Directory not contains Poco file!", out.getvalue().strip())

    def test_add_and_remove(self):
        self.init_with_local_catalog()
        test_dir = os.path.join(self.tmpdir, "test-directory")
        os.makedirs(test_dir)
        git.Repo.clone_from(url=AbstractTestSuite.STACK_LIST_SAMPLE['nginx']['git'], to_path=test_dir)
        os.rename(os.path.join(test_dir, 'nginx', 'poco.yml'), os.path.join(test_dir, 'poco.yml'))
        with self.captured_output() as (out, err):
            self.run_poco_command("project", "add", test_dir)
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn("Project added", out.getvalue())
        self.clean_states()
        with self.captured_output() as (out, err):
            self.run_poco_command("catalog")
        self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())
        self.assertIn("test-directory", out.getvalue())
        self.clean_states()
        with self.captured_output() as (out, err):
            self.run_poco_command("project", "remove", "test-directory")
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn("Project removed", out.getvalue())
        self.clean_states()
        with self.captured_output() as (out, err):
            self.run_poco_command("catalog")
        self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())
        self.assertNotIn("test-directory", out.getvalue())

    def test_init_without_catalog(self):
        self.init_with_local_catalog()
        self.assertIsNone(FileUtils.get_file_with_extension('poco', directory=self.ws_dir))
        self.assertIsNone(FileUtils.get_file_with_extension('docker-compose', directory=self.ws_dir))
        with self.captured_output() as (out, err):
            self.run_poco_command("project", "init")
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIsNotNone(FileUtils.get_file_with_extension('poco', directory=self.ws_dir))
        self.assertIsNotNone(FileUtils.get_file_with_extension('docker-compose', directory=self.ws_dir))

    def test_checkout(self):
        self.init_with_remote_catalog()
        base_dir = os.path.join(self.ws_dir, 'poco-example')
        directory = os.path.join(base_dir, 'nginx')
        self.assertFalse(os.path.exists(directory))
        with self.captured_output() as (out, err):
            self.run_poco_command("checkout", "nginx")
        self.assertIn("Project checkout complete " + base_dir, out.getvalue().strip())
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertTrue(os.path.exists(directory))

    def test_install(self):
        self.init_with_remote_catalog()
        base_dir = os.path.join(self.ws_dir, 'poco-example')
        directory = os.path.join(base_dir, 'nginx')
        self.assertFalse(os.path.exists(directory))
        with self.captured_output() as (out, err):
            self.run_poco_command("install", "nginx")
        self.assertIn("Install completed to " + base_dir, out.getvalue().strip())
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertTrue(os.path.exists(directory))

    def test_install_with_before_script(self):
        self.init_with_remote_catalog()
        base_dir = os.path.join(self.ws_dir, 'poco-example')
        dir = os.path.join(base_dir, 'nginx')
        self.assertFalse(os.path.exists(dir))
        with self.captured_output() as (out, err):
            self.run_poco_command("install", "nginx")
        self.assertIn("Install completed to " + base_dir, out.getvalue().strip())
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertTrue(os.path.exists(dir))

    def test_plan_list_with_not_exists_project(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            with self.assertRaises(SystemExit) as context:
                self.run_poco_command("plan", "ls")
            self.assertIsNotNone(context.exception)
        self.assertIn("Poco file not found in directory:", out.getvalue())

    def test_plan_list(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("plan", "ls", "nginx")
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("default", out.getvalue())
        self.assertIn("demo/hello", out.getvalue())

    def test_branches(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("branches", "nginx")
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("master", out.getvalue())

    def test_branch_without_change_branch(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            self.run_poco_command("install", "nginx")
        self.assertIn("Install completed to ", out.getvalue().strip())
        self.assertEqual(0, len(err.getvalue().strip()))
        with self.captured_output() as (out, err):
            self.run_poco_command("branch", "mysql", "master")
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("Branch changed", out.getvalue())
