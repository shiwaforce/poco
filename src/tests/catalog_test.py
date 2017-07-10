# -*- coding: utf-8 -*-

import os
import yaml
import git
from src.catalog import ProjectCatalog
from docopt import DocoptExit
from .abstract_test import AbstractTestSuite


class CatalogTestSuite(AbstractTestSuite):

    def test_without_command(self):
        with self.assertRaises(DocoptExit) as context:
            catalog = ProjectCatalog(home_dir=self.tmpdir)
            catalog.run([""])
        self.assertIsNotNone(context.exception)

    def test_init(self):
        catalog = ProjectCatalog(home_dir=self.tmpdir)
        with self.captured_output() as (out, err):
            catalog.run(["init"])
        self.assertIn("Init completed", out.getvalue().strip())
        with open(self.config_file, 'r') as stream:
            self.assertIn("default:\n  workspace:", stream.read())

    def test_init_with_params(self):
        catalog = ProjectCatalog(home_dir=self.tmpdir)
        with self.captured_output() as (out, err):
            catalog.run(["init", "url", "git", "compose-file-with-another-name"])
        self.assertIn("Init completed", out.getvalue().strip())
        with open(self.config_file, 'r') as stream:
            config = stream.read()
            self.assertIn("default:\n ", config)
            self.assertIn("repositoryType: git", config)
            self.assertIn("server: url", config)
            self.assertIn("file: compose-file-with-another-name", config)

    def test_wrong_parameters(self):
        with self.assertRaises(DocoptExit) as context:
            catalog = ProjectCatalog(home_dir=self.tmpdir)
            catalog.run(["notexistcommand"])
        self.assertIsNotNone(context.exception)

    def test_config_without_config(self):
        with self.assertRaises(SystemExit) as context:
            catalog = ProjectCatalog(home_dir=self.tmpdir)
            catalog.run(["config"])
        self.assertIsNotNone(context.exception)

    def test_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir)
            catalog.run(["config"])
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn(yaml.dump(data=AbstractTestSuite.REMOTE_CONFIG, default_flow_style=False, default_style='',
                                indent=4).strip(), out.getvalue().strip())

    def test_list_with_local_config(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir)
            catalog.run(["ls"])
        self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())

    def test_list_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir)
            catalog.run(["ls"])
        self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())

    def test_branches_with_local_config(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir)
            catalog.run(["branches"])
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn('Available branches in', out.getvalue().strip())
        self.assertNotIn('master', out.getvalue().strip())

    def test_branches_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir)
            catalog.run(["branches"])
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn('Available branches in', out.getvalue().strip())
        self.assertIn('master', out.getvalue().strip())

    def test_switch_branch_with_local_config(self):
        self.init_with_local_catalog()
        with self.assertRaises(SystemExit) as context:
            catalog = ProjectCatalog(home_dir=self.tmpdir)
            catalog.run(["branch", "master"])
        self.assertEqual(1, context.exception.code)

    def test_switch_branch_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir)
            catalog.run(["branch", "master"])
        self.assertIn("Branch changed", out.getvalue())

    def test_push_with_local_config(self):
        self.init_with_local_catalog()
        catalog = ProjectCatalog(home_dir=self.tmpdir)
        with self.captured_output() as (out, err):
            catalog.run(["push"])
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn("Push completed", out.getvalue())

    def test_add_and_remove(self):
        self.init_with_local_catalog()
        test_dir = os.path.join(self.tmpdir, "test-directory")
        os.makedirs(test_dir)
        git.Repo.clone_from(url=AbstractTestSuite.STACK_LIST_SAMPLE['nginx']['git'], to_path=test_dir)
        catalog = ProjectCatalog(home_dir=self.tmpdir)
        with self.captured_output() as (out, err):
            catalog.run(["add", test_dir])
        self.assertIn("Project added", out.getvalue())
        with self.captured_output() as (out, err):
            catalog.run(["ls"])
            self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())
        self.assertIn("test-directory", out.getvalue())
        with self.captured_output() as (out, err):
            catalog.run(["remove", "test-directory"])
        self.assertIn("Project removed", out.getvalue())
        with self.captured_output() as (out, err):
            catalog.run(["ls"])
            self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())
        self.assertNotIn("test-directory", out.getvalue())
