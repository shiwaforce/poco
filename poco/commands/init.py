import os
import shutil
from .abstract_command import AbstractCommand
from ..services.console_logger import ColorPrint
from ..services.state_utils import StateUtils
from ..services.file_utils import FileUtils
from ..services.project_utils import ProjectUtils
from ..services.state import StateHolder


class Init(AbstractCommand):

    command = "init"
    args = ["[<name>]", "[--with-cursor-skill]"]
    args_descriptions = {
        "[<name>]": "Name of the project or the actual directory if it is empty",
        "[--with-cursor-skill]": "Create .cursor/skills/poco-project/SKILL.md for AI agents (Cursor, etc.)",
    }
    description = "Run: 'poco init nginx' or 'poco project init nginx' to initialize poco project, poco.yml " \
                  "and docker-compose.yml will be created if they don't exist in nginx project directory"
    options_doc = "\n  --with-cursor-skill  Create .cursor/skills/poco-project/SKILL.md for AI agents."

    def prepare_states(self):
        StateHolder.work_dir = StateHolder.base_work_dir
        StateHolder.name = FileUtils.get_parameter_or_directory_name('<name>')
        StateUtils.prepare("project_repo")

    def resolve_dependencies(self):
        pass

    def execute(self):
        target_dir = None
        if StateHolder.repository is not None:
            target_file = os.path.join(ProjectUtils.get_target_dir(StateHolder.catalog_element),
                                       StateHolder.catalog_element.get('file', 'poco.yml'))
            if not os.path.exists(target_file):
                Init.fix_file(target_file)
                target_dir = os.path.dirname(target_file)
        else:
            file = FileUtils.get_backward_compatible_poco_file(directory=os.getcwd())
            if file is None:
                poco_yml = os.path.join(os.getcwd(), 'poco.yml')
                Init.fix_file(poco_yml)
                target_dir = os.getcwd()

        if target_dir is not None:
            args_list = StateHolder.args.get("<args>") or []
            if "--with-cursor-skill" in args_list:
                Init.write_cursor_skill(target_dir)

        ColorPrint.print_info("Project init completed")

    @staticmethod
    def fix_file(target_file):
        if not os.path.exists(target_file):
            src_file = os.path.join(os.path.dirname(__file__), '../services/resources/poco.yml')
            shutil.copyfile(src=src_file, dst=target_file)
            default_compose = os.path.join(os.path.dirname(target_file), 'docker-compose.yml')
            if not os.path.exists(default_compose):
                src_file = os.path.join(os.path.dirname(__file__), '../services/resources/docker-compose.yml')
                shutil.copyfile(src=src_file, dst=default_compose)

    @staticmethod
    def write_cursor_skill(target_dir):
        """Create .cursor/skills/poco-project/SKILL.md for AI agents."""
        skill_dir = os.path.join(target_dir, ".cursor", "skills", "poco-project")
        os.makedirs(skill_dir, exist_ok=True)
        skill_file = os.path.join(skill_dir, "SKILL.md")
        content = """---
name: poco-project
description: Project-specific poco setup. Use when working in this repository and running compose or poco commands.
---
# Poco project

This project uses [Poco](https://github.com/shiwaforce/poco) for Docker Compose.

- **Config:** `poco.yml` in this directory (and optionally `docker-compose.yml`).
- **Plan:** Typically `default`; run `poco plan` to see or switch.
- **Suggested commands:** `poco up`, `poco down`, `poco status`, `poco ps`.

For full poco reference (all commands, options, catalog, presets), use the poco skill from **shiwaforce/poco-skills** (Cursor: Settings > Rules > Add Rule > Remote Rule (Github) `shiwaforce/poco-skills`).
"""
        with open(skill_file, "w", encoding="utf-8") as f:
            f.write(content)
        ColorPrint.print_info("Created " + skill_file, lvl=-1)
