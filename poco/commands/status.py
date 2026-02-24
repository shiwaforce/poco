"""poco status — list Docker Compose projects currently running (overview from any directory)."""
import subprocess
from .abstract_command import AbstractCommand
from ..services.state import StateHolder
from ..services.state_utils import StateUtils
from ..services.environment_utils import EnvironmentUtils
from ..services.console_logger import ColorPrint


class Status(AbstractCommand):

    command = "status"
    args = ["[-a]"]
    args_descriptions = {"[-a]": "Include stopped compose projects."}
    description = "Show Docker Compose projects currently running (overview; run from any directory)."
    options_doc = "\n  -a, --all    Include stopped compose projects."

    def prepare_states(self):
        StateUtils.prepare("config")

    def resolve_dependencies(self):
        EnvironmentUtils.check_docker()

    def execute(self):
        show_all = StateHolder.args.get("-a", False) or StateHolder.args.get("--all", False)
        cmd = ["docker", "compose", "ls"]
        if show_all:
            cmd.append("-a")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            ColorPrint.print_error("Failed to list compose projects: " + str(e))
            return
        out = (result.stdout or "").strip()
        err = (result.stderr or "").strip()
        if result.returncode != 0:
            ColorPrint.print_error(err or "docker compose ls failed")
            return
        lines = [ln.strip() for ln in out.split("\n") if ln.strip()]
        if not lines or (len(lines) == 1 and lines[0].upper().startswith("NAME")):
            if show_all:
                ColorPrint.print_info("No Docker Compose projects found.", lvl=-1)
            else:
                ColorPrint.print_info(
                    "No Docker Compose projects currently running.\n  Use 'poco status -a' to include stopped.",
                    lvl=-1,
                )
            return
        ColorPrint.print_info("Docker Compose projects currently running:" if not show_all else "Docker Compose projects (all):", lvl=-1)
        print(out)
