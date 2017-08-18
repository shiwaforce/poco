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
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=[""])
            catalog.run()
        self.assertIsNotNone(context.exception)

    def test_wrong_parameters(self):
        with self.assertRaises(DocoptExit) as context:
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["notexistcommand"])
            catalog.run()
        self.assertIsNotNone(context.exception)

    def test_config_without_config(self):
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["config"])
            catalog.run()
        self.assertEqual(0, len(err.getvalue()))
        AbstractTestSuite.REMOTE_CONFIG['default'].pop('workspace')
        self.assertIn(yaml.dump(data=AbstractTestSuite.REMOTE_CONFIG, default_flow_style=False, default_style='',
                                indent=4).strip(), out.getvalue().strip())

    def test_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["config"])
            catalog.run()
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn(yaml.dump(data=AbstractTestSuite.REMOTE_CONFIG, default_flow_style=False, default_style='',
                                indent=4).strip(), out.getvalue().strip())

    def test_list_with_local_config(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["ls"])
            catalog.run()
        self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())

    def test_list_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["ls"])
            catalog.run()
        self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())

    def test_branches_with_local_config(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["branches"])
            catalog.run()
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn('Available branches in', out.getvalue().strip())
        self.assertNotIn('master', out.getvalue().strip())

    def test_branches_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["branches"])
            catalog.run()
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn('Available branches in', out.getvalue().strip())
        self.assertIn('master', out.getvalue().strip())

    def test_switch_branch_with_local_config(self):
        self.init_with_local_catalog()
        with self.assertRaises(SystemExit) as context:
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["branch", "master"])
            catalog.run()
        self.assertEqual(1, context.exception.code)

    def test_switch_branch_with_remote_config(self):
        self.init_with_remote_catalog()
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["branch", "master"])
            catalog.run()
        self.assertIn("Branch changed", out.getvalue())

    def test_push_with_local_config(self):
        self.init_with_local_catalog()
        catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["push"])
        with self.captured_output() as (out, err):
            catalog.run()
        self.assertEqual(0, len(err.getvalue().strip()))
        self.assertIn("Push completed", out.getvalue())

    def test_add_and_remove(self):
        self.init_with_local_catalog()
        test_dir = os.path.join(self.tmpdir, "test-directory")
        os.makedirs(test_dir)
        git.Repo.clone_from(url=AbstractTestSuite.STACK_LIST_SAMPLE['nginx']['git'], to_path=test_dir)
        catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["add", test_dir])
        with self.captured_output() as (out, err):
            catalog.run()
        self.assertIn("Project added", out.getvalue())
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["ls"])
            catalog.run()
            self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())
        self.assertIn("test-directory", out.getvalue())
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["remove", "test-directory"])
            catalog.run()
        self.assertIn("Project removed", out.getvalue())
        with self.captured_output() as (out, err):
            catalog = ProjectCatalog(home_dir=self.tmpdir, skip_docker=True, argv=["ls"])
            catalog.run()
            self.assertEqual(0, len(err.getvalue().strip()))
        for key in AbstractTestSuite.STACK_LIST_SAMPLE.keys():
            self.assertTrue(key in out.getvalue().strip())
        self.assertNotIn("test-directory", out.getvalue())
