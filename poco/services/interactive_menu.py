"""Interactive menu for poco: choose actions without typing commands."""
from .state import StateHolder
from .state_utils import StateUtils
from .console_logger import ColorPrint
from .interactive import choose_one

# ANSI for menu headers (independent of ColorPrint log level)
_MENU_HEADER = "\033[1;36m"
_RESET = "\033[0m"


def _option_flags():
    """Build list of global flags to pass when invoking a sub-command from the menu."""
    flags = []
    if StateHolder.args.get("--verbose"):
        flags.append("-V")
    if StateHolder.args.get("--no-matrix"):
        flags.append("--no-matrix")
    if StateHolder.args.get("--quiet"):
        flags.append("-q")
    return flags


def _run_one_command(poco, argv):
    """Set argv, run check_command, then run the command state machine until done.
    If the command exits (e.g. nothing to show, not configured), catch and return to menu."""
    flags = _option_flags()
    poco.argv = argv + flags
    try:
        poco.check_command()
        if poco.active_object is None:
            return
        counter = 0
        while counter < 10:
            counter += 1
            if poco.inner_flow():
                break
    except SystemExit:
        # Command exited (empty result, error, or sys.exit). Stay in interactive menu.
        print()
        ColorPrint.print_info("Nothing to show or not configured. Returning to menu.")
        print()


def _main_menu():
    return [
        "Start project (up)",
        "Stop project (down)",
        "Project status (ps)",
        "Kubernetes (kubectx, kubens, kube-get, preset)",
        "Helm (repos, list)",
        "Catalog (list projects)",
        "Quit",
    ]


def _kubernetes_menu():
    return [
        "Switch context (kubectx) – choose interactively",
        "Switch namespace (kubens) – choose interactively",
        "Get resources (kube-get pods / ns / …)",
        "Preset: list / use / save",
        "Back",
    ]


def _helm_menu():
    return [
        "List repos (helm-repos)",
        "List releases (helm-list)",
        "List releases – pick one and show status (helm-list -i)",
        "Back",
    ]


def _preset_menu():
    return [
        "List presets",
        "Use preset (switch context + namespace)",
        "Save current context + namespace as preset",
        "Back",
    ]


def _get_project_choices():
    """Load catalog and return list of project[/plan] strings for menu."""
    try:
        StateUtils.prepare("catalog")
    except Exception:
        return []
    if not StateHolder.catalogs:
        return []
    choices = []
    for cat_name, projects in StateHolder.catalogs.items():
        if not isinstance(projects, dict):
            continue
        for proj_name in projects.keys():
            if cat_name and cat_name != "default":
                choices.append("%s / %s" % (cat_name, proj_name))
            else:
                choices.append(proj_name)
    return sorted(choices)


def run_interactive_menu(poco):
    """Show interactive menu in a loop; run chosen commands without requiring command-line knowledge."""
    while True:
        print()
        print(_MENU_HEADER + "  POCO — Interactive menu" + _RESET)
        print("  " + "-" * 40)
        choice = choose_one(
            _main_menu(),
            prompt="Choose action (number or Enter to cancel): ",
            title="Main",
        )
        if not choice:
            return
        if choice == "Quit":
            return
        if choice == "Start project (up)":
            projects = _get_project_choices()
            if not projects:
                ColorPrint.print_info("No projects in catalog. Add repos and projects first (e.g. poco repo add, poco project add).")
                continue
            proj = choose_one(projects, prompt="Choose project: ", title="Start project")
            if proj:
                _run_one_command(poco, ["up", proj])
            continue
        if choice == "Stop project (down)":
            projects = _get_project_choices()
            if not projects:
                ColorPrint.print_info("No projects in catalog.")
                continue
            proj = choose_one(projects, prompt="Choose project: ", title="Stop project")
            if proj:
                _run_one_command(poco, ["down", proj])
            continue
        if choice == "Project status (ps)":
            projects = _get_project_choices()
            if not projects:
                ColorPrint.print_info("No projects in catalog.")
                continue
            proj = choose_one(projects, prompt="Choose project: ", title="Project status")
            if proj:
                _run_one_command(poco, ["ps", proj])
            continue
        if choice == "Kubernetes (kubectx, kubens, kube-get, preset)":
            k8s = choose_one(_kubernetes_menu(), prompt="Kubernetes: ", title="Kubernetes")
            if not k8s or k8s == "Back":
                continue
            if "kubectx" in k8s:
                _run_one_command(poco, ["kubectx", "-i"])
            elif "kubens" in k8s:
                _run_one_command(poco, ["kubens", "-i"])
            elif "Get resources" in k8s:
                res = choose_one(["pods", "ns", "svc", "deploy", "nodes"], prompt="Resource type: ", title="kube-get")
                if res:
                    _run_one_command(poco, ["kube-get", res])
            elif "Preset" in k8s:
                preset_choice = choose_one(_preset_menu(), prompt="Preset: ", title="Preset")
                if not preset_choice or preset_choice == "Back":
                    continue
                if "List" in preset_choice:
                    _run_one_command(poco, ["preset", "list"])
                elif "Use" in preset_choice:
                    _run_one_command(poco, ["preset", "use", "-i"])
                elif "Save" in preset_choice:
                    name = input("Preset name to save: ").strip()
                    if name:
                        _run_one_command(poco, ["preset", "save", name])
            continue
        if choice == "Helm (repos, list)":
            helm_choice = choose_one(_helm_menu(), prompt="Helm: ", title="Helm")
            if not helm_choice or helm_choice == "Back":
                continue
            if "repos" in helm_choice.lower():
                _run_one_command(poco, ["helm-repos"])
            elif "List releases" in helm_choice and "-i" in helm_choice:
                _run_one_command(poco, ["helm-list", "-i"])
            elif "List releases" in helm_choice:
                _run_one_command(poco, ["helm-list"])
            continue
        if choice == "Catalog (list projects)":
            _run_one_command(poco, ["catalog"])
            continue
