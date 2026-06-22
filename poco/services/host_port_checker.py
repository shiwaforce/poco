import os
import platform
import re
import shutil
import sys
from subprocess import Popen, PIPE

import yaml

from .console_logger import ColorPrint
from .environment_utils import EnvironmentUtils
from .yaml_utils import YamlUtils


class PortConflict(object):

    def __init__(self, message):
        self.message = message


def format_conflict_message(project_name, plan_name, conflict_lines, duplicate_lines, stop_hints):
    parts = [
        'Cannot start project "' + str(project_name) + '" with plan "' + str(plan_name) + '".',
        "",
    ]
    if duplicate_lines:
        parts.append("Duplicate host ports in plan:")
        parts.extend(duplicate_lines)
        parts.append("")
    if conflict_lines:
        parts.append("Host port conflicts:")
        parts.extend(conflict_lines)
        parts.append("")
    if stop_hints:
        unique_hints = []
        for hint in stop_hints:
            if hint not in unique_hints:
                unique_hints.append(hint)
        for hint in unique_hints:
            parts.append(hint)
    return "\n".join(parts).rstrip() + "\n"


def parse_host_port_from_entry(port_entry):
    """Return host port integer from a merged compose ports entry, or None if not host-published."""
    if port_entry is None:
        return None
    if isinstance(port_entry, int):
        return None
    if isinstance(port_entry, dict):
        published = port_entry.get("published")
        if published is None:
            return None
        try:
            value = int(str(published).strip().strip('"').strip("'"))
        except (TypeError, ValueError):
            return None
        if value <= 0:
            return None
        return value
    text = str(port_entry).strip().strip('"').strip("'")
    if not text:
        return None
    segments = text.split(":")
    if len(segments) == 1:
        return None
    if len(segments) == 2:
        host_segment = segments[0]
    elif len(segments) == 3:
        host_segment = segments[1]
    else:
        return None
    try:
        value = int(host_segment.strip())
    except (TypeError, ValueError):
        return None
    if value <= 0:
        return None
    return value


def extract_host_ports_from_merged_config(merged_config_text):
    """Build map of host_port -> list of service names from merged compose YAML."""
    try:
        config = yaml.load(merged_config_text, Loader=YamlUtils.loader)
    except yaml.YAMLError:
        return None
    if not isinstance(config, dict):
        return None
    services = config.get("services")
    if not isinstance(services, dict):
        return {}
    port_map = {}
    for service_name, service_config in services.items():
        if not isinstance(service_config, dict):
            continue
        port_list = service_config.get("ports")
        if not port_list:
            continue
        for port_entry in port_list:
            host_port = parse_host_port_from_entry(port_entry)
            if host_port is None:
                continue
            port_map.setdefault(host_port, [])
            if service_name not in port_map[host_port]:
                port_map[host_port].append(service_name)
    return port_map


def find_duplicate_host_ports(port_map):
    """Return lines describing services that share the same host port in the plan."""
    lines = []
    for host_port, service_names in sorted(port_map.items()):
        if len(service_names) > 1:
            lines.append(
                "  Port " + str(host_port) + ": " + ", ".join(service_names)
            )
    return lines


def _is_windows_command_prompt_env(runtime_platform, environ):
    """Detect Windows cmd.exe shell from platform and environment (testable without mocking sys)."""
    if runtime_platform != "win32":
        return False
    if environ.get("MSYSTEM"):
        return False
    if environ.get("PSModulePath") or environ.get("POWERSHELL_DISTRIBUTION_CHANNEL"):
        return False
    comspec = (environ.get("COMSPEC") or "").lower()
    return comspec.endswith("cmd.exe") or comspec.endswith("\\cmd.exe")


def is_windows_command_prompt():
    return _is_windows_command_prompt_env(sys.platform, os.environ)


def socket_check_command(host_port):
    system = platform.system().lower()
    if is_windows_command_prompt():
        return None
    if system == "linux" or system == "windows":
        if shutil.which("ss"):
            return ["ss", "-tlnH", "sport", "=", ":" + str(host_port)]
    if system == "darwin":
        if shutil.which("lsof"):
            return ["lsof", "-nP", "-iTCP:" + str(host_port), "-sTCP:LISTEN"]
    if system == "windows" and shutil.which("netstat"):
        return ["netstat", "-ano"]
    if system == "linux" and shutil.which("netstat"):
        return ["netstat", "-tln"]
    return None


def run_command_output(command):
    if not command:
        return None, False
    try:
        process = Popen(command, stdout=PIPE, stderr=PIPE, shell=isinstance(command, str))
        out, err = process.communicate()
        if process.returncode not in (0, 1):
            return None, False
        text = EnvironmentUtils.decode(out if out else err)
        return text, True
    except (OSError, ValueError):
        return None, False


def is_port_listening_via_socket(host_port):
    command = socket_check_command(host_port)
    if command is None:
        return None, None
    if command[0] == "netstat":
        output, ok = run_command_output(command)
        if not ok or output is None:
            return None, None
        pattern = re.compile(r"[:.]" + str(host_port) + r"\s")
        for line in output.splitlines():
            if "LISTEN" in line.upper() and pattern.search(line):
                detail = line.strip()
                if len(detail) > 120:
                    detail = detail[:117] + "..."
                return True, detail
        return False, None
    output, ok = run_command_output(command)
    if not ok:
        return None, None
    if output and output.strip():
        first_line = output.strip().splitlines()[0].strip()
        return True, first_line
    return False, None


def query_docker_publishers(host_port):
    command = (
        'docker ps --filter "publish=' + str(host_port) + '" '
        '--format "{{.Names}}\t{{.Label \\"com.docker.compose.project\\"}}\t{{.Image}}"'
    )
    output, ok = run_command_output(command)
    if not ok:
        return None
    publishers = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        name = parts[0] if len(parts) > 0 else "unknown"
        project = parts[1] if len(parts) > 1 else ""
        image = parts[2] if len(parts) > 2 else ""
        publishers.append({
            "name": name,
            "project": project,
            "image": image,
        })
    return publishers


def docker_check_available():
    return shutil.which("docker") is not None


def socket_tool_name():
    system = platform.system().lower()
    if is_windows_command_prompt():
        return None
    if system == "linux" or system == "windows":
        if shutil.which("ss"):
            return "ss"
    if system == "darwin":
        if shutil.which("lsof"):
            return "lsof"
    if shutil.which("netstat"):
        return "netstat"
    return None


class HostPortChecker(object):

    def __init__(self, project_name, plan_name, merged_config_text):
        self.project_name = project_name
        self.plan_name = plan_name
        self.merged_config_text = merged_config_text

    def run(self):
        ColorPrint.print_info("Checking host ports...")
        port_map = extract_host_ports_from_merged_config(self.merged_config_text)
        if port_map is None:
            self._print_skipped(
                "Host port preflight skipped: could not parse merged docker compose config.\n"
                "Continuing startup - port conflicts may only appear from Docker later."
            )
            return None

        duplicate_lines = find_duplicate_host_ports(port_map)
        if duplicate_lines:
            message = format_conflict_message(
                self.project_name,
                self.plan_name,
                [],
                duplicate_lines,
                [],
            )
            return PortConflict(message)

        if not port_map:
            ColorPrint.print_info("Host port check passed.")
            return None

        docker_available = docker_check_available()
        socket_tool = socket_tool_name()
        if not docker_available and socket_tool is None:
            self._print_skipped(
                "Host port preflight skipped: neither docker nor socket tools "
                "(ss, lsof, netstat) are available.\n"
                "Continuing startup - port conflicts may only appear from Docker later."
            )
            return None

        if not docker_available and socket_tool is not None:
            ColorPrint.print_warning(
                "Host port preflight partial: docker is not available.\n"
                "Checked socket listeners only (" + socket_tool + ")."
            )

        if docker_available and socket_tool is None:
            ColorPrint.print_warning(
                "Host port preflight partial: socket listener check unavailable "
                "(" + self._missing_socket_tool_label() + ").\n"
                "Checked Docker-published ports only."
            )

        conflict_lines = []
        stop_hints = []
        checked_any = False

        for host_port in sorted(port_map.keys()):
            port_conflict = self._check_single_port(
                host_port,
                docker_available=docker_available,
                socket_tool=socket_tool,
            )
            if port_conflict is None:
                continue
            if port_conflict == "unchecked":
                continue
            checked_any = True
            conflict_lines.extend(port_conflict["lines"])
            if port_conflict.get("stop_hint"):
                stop_hints.append(port_conflict["stop_hint"])

        if conflict_lines:
            message = format_conflict_message(
                self.project_name,
                self.plan_name,
                conflict_lines,
                [],
                stop_hints,
            )
            return PortConflict(message)

        if not checked_any and not docker_available:
            self._print_skipped(
                "Host port preflight skipped: could not verify any host ports.\n"
                "Continuing startup - port conflicts may only appear from Docker later."
            )
            return None

        ColorPrint.print_info("Host port check passed.")
        return None

    def _missing_socket_tool_label(self):
        system = platform.system().lower()
        if system == "darwin":
            return "lsof not found"
        if system == "linux":
            return "ss not found"
        if is_windows_command_prompt():
            return "socket tools unavailable in cmd.exe"
        return "ss/lsof/netstat not found"

    def _print_skipped(self, message):
        ColorPrint.print_warning(message)

    def _check_single_port(self, host_port, docker_available, socket_tool):
        foreign_publishers = []
        own_publishers = []

        if docker_available:
            publishers = query_docker_publishers(host_port)
            if publishers is None:
                return "unchecked"
            for publisher in publishers:
                project = publisher.get("project") or ""
                if project == self.project_name:
                    own_publishers.append(publisher)
                else:
                    foreign_publishers.append(publisher)

        if foreign_publishers:
            lines = ["  Port " + str(host_port) + ":"]
            for publisher in foreign_publishers:
                lines.append("    container: " + publisher["name"])
                if publisher.get("project"):
                    lines.append("    project:   " + publisher["project"])
                if publisher.get("image"):
                    lines.append("    image:     " + publisher["image"])
            stop_hint = None
            first_project = foreign_publishers[0].get("project")
            if first_project:
                stop_hint = (
                    'Stop the conflicting stack: poco down '
                    '(compose project "' + first_project + '")'
                )
            return {"lines": lines, "stop_hint": stop_hint}

        if own_publishers:
            return None

        if socket_tool is None:
            return None

        listening, detail = is_port_listening_via_socket(host_port)
        if listening is None:
            return "unchecked"
        if listening:
            lines = [
                "  Port " + str(host_port) + ":",
                "    listener:  unknown (port in use, not published by Docker)",
            ]
            if detail:
                lines.append("    detail:    " + detail)
            return {"lines": lines, "stop_hint": None}

        return None


def print_port_conflict_at_end(conflict, tty_stream=None):
    """Write conflict message to real stdout/stderr and optional TTY stream."""
    message = conflict.message if isinstance(conflict, PortConflict) else str(conflict)
    ColorPrint.print_error("\n" + message.strip() + "\n")
    if tty_stream is not None:
        try:
            tty_stream.write("\n" + message)
            tty_stream.flush()
        except (OSError, BrokenPipeError):
            pass
