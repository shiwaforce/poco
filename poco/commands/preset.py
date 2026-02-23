"""Preset commands: list, use, save (kubectl context + namespace)."""
from .abstract_command import AbstractCommand
from ..services.state_utils import StateUtils
from ..services.state import StateHolder
from ..services.console_logger import ColorPrint
from ..services.environment_utils import EnvironmentUtils
from ..services.preset_store import load_presets, save_presets
import subprocess


class PresetList(AbstractCommand):

    sub_command = "preset"
    command = "list"
    args = []
    args_descriptions = {}
    description = "Run: 'poco preset list' to list saved context+namespace presets."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        pass

    def execute(self):
        presets = load_presets()
        if not presets:
            ColorPrint.print_info("No presets. Save one with: poco preset save <name>")
            return
        for name, data in presets.items():
            if isinstance(data, dict):
                ctx = data.get("context", "")
                ns = data.get("namespace", "")
                ColorPrint.print_with_lvl(message="%s  context=%s  namespace=%s" % (name, ctx, ns), lvl=-1)
            else:
                ColorPrint.print_with_lvl(message=str(name), lvl=-1)


class PresetUse(AbstractCommand):

    sub_command = "preset"
    command = "use"
    args = ["[<name>]", "[-i]", "[--choose]"]
    args_descriptions = {
        "[<name>]": "Preset name to switch to.",
        "[-i]": "Interactive: choose preset from menu/fzf.",
        "[--choose]": "Same as -i.",
    }
    description = "Run: 'poco preset use <name>' to switch to a preset. Use -i to choose from list."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        EnvironmentUtils.check_kubernetes()

    def execute(self):
        from ..services.interactive import choose_one
        name = StateHolder.args.get("<name>")
        interactive = StateHolder.args.get("-i") or StateHolder.args.get("--choose")
        if not name and interactive:
            presets = load_presets()
            if not presets:
                ColorPrint.print_info("No presets. Save one with: poco preset save <name>")
                return
            lines = list(presets.keys())
            name = choose_one(lines, prompt="Preset number: ")
            if not name:
                return
        if not name:
            ColorPrint.exit_after_print_messages(message="Preset name required. Use 'poco preset list' or -i to choose.")
        presets = load_presets()
        if name not in presets:
            ColorPrint.exit_after_print_messages(message="Preset not found: %s. Use 'poco preset list'." % name)
        data = presets[name]
        if not isinstance(data, dict):
            ColorPrint.exit_after_print_messages(message="Invalid preset: %s" % name)
        context = data.get("context")
        namespace = data.get("namespace")
        if context:
            rc = subprocess.run(["kubectl", "config", "use-context", context], shell=False)
            if rc.returncode != 0:
                ColorPrint.exit_after_print_messages(message="Failed to switch context: %s" % context)
            ColorPrint.print_info("Context: %s" % context)
        if namespace:
            rc = subprocess.run(
                ["kubectl", "config", "set-context", "--current", "--namespace=" + namespace],
                shell=False,
            )
            if rc.returncode != 0:
                ColorPrint.exit_after_print_messages(message="Failed to set namespace: %s" % namespace)
            ColorPrint.print_info("Namespace: %s" % namespace)
        if not context and not namespace:
            ColorPrint.print_info("Preset '%s' has no context or namespace." % name)


class PresetSave(AbstractCommand):

    sub_command = "preset"
    command = "save"
    args = ["<name>"]
    args_descriptions = {"<name>": "Name to save the current context and namespace as."}
    description = "Run: 'poco preset save <name>' to save current kubectl context and namespace as a preset."

    def prepare_states(self):
        StateUtils.prepare("config")
        StateHolder.work_dir = StateHolder.base_work_dir

    def resolve_dependencies(self):
        EnvironmentUtils.check_kubernetes()

    def execute(self):
        name = StateHolder.args.get("<name>")
        if not name:
            ColorPrint.exit_after_print_messages(message="Preset name required.")
        ctx_out = subprocess.run(
            ["kubectl", "config", "current-context"],
            capture_output=True,
            text=True,
            shell=False,
        )
        context = ctx_out.stdout.strip() if ctx_out.returncode == 0 and ctx_out.stdout else ""
        ns_out = subprocess.run(
            ["kubectl", "config", "view", "--minify", "-o", "jsonpath={..namespace}"],
            capture_output=True,
            text=True,
            shell=False,
        )
        namespace = (ns_out.stdout.strip() or "default") if ns_out.returncode == 0 else "default"
        presets = load_presets()
        presets[name] = {"context": context, "namespace": namespace}
        save_presets(presets)
        ColorPrint.print_info("Saved preset '%s': context=%s, namespace=%s" % (name, context, namespace))
