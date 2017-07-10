import git
import os
from docopt import DocoptExit
from .abstract_test import AbstractTestSuite
from src.compose import ProjectCompose
from src.catalog import ProjectCatalog


class ComposeTestSuite(AbstractTestSuite):

    def test_without_command(self):
        with self.assertRaises(DocoptExit) as context:
            compose = ProjectCompose(home_dir=self.tmpdir)
            compose.run([""])
        self.assertIsNotNone(context.exception)

    def test_mode_list(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            compose = ProjectCompose(home_dir=self.tmpdir)
            compose.run(["mode", "ls", "mysql"])
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("default", out.getvalue())

    def test_branches(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            compose = ProjectCompose(home_dir=self.tmpdir)
            compose.run(["branches", "mysql"])
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("master", out.getvalue())

    def test_branch_without_change_branch(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            compose = ProjectCompose(home_dir=self.tmpdir)
            compose.run(["branch", "mysql", "master"])
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("Branch changed", out.getvalue())

    def test_init(self):
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
        with self.captured_output() as (out, err):
            compose = ProjectCompose(home_dir=self.tmpdir)
            compose.run(["init", "test-directory"])
        self.assertEqual(0, len(err.getvalue()))
        self.assertIn("Project init completed", out.getvalue())
        self.assertTrue(os.path.exists(self.ws_dir))
        self.assertTrue(os.path.exists(os.path.join(self.ws_dir, "test-directory")))
        self.assertTrue(os.path.exists(os.path.join(self.ws_dir, "test-directory/project-compose.yml")))
        self.assertTrue(os.path.exists(os.path.join(self.ws_dir, "test-directory/docker-compose.yml")))

    def test_install(self):
        self.init_with_local_catalog()
        with self.captured_output() as (out, err):
            compose = ProjectCompose(home_dir=self.tmpdir)
            compose.run(["install", "mysql"])
        self.assertEqual(0, len(err.getvalue()))
        self.assertTrue(os.path.exists(self.ws_dir))
        self.assertTrue(os.path.exists(os.path.join(self.ws_dir, "project-compose-example")))