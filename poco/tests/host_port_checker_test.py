import os
import unittest
from io import StringIO
from unittest import mock

from poco.services.host_port_checker import (
    PortConflict,
    HostPortChecker,
    extract_host_ports_from_merged_config,
    find_duplicate_host_ports,
    format_conflict_message,
    is_windows_command_prompt,
    parse_host_port_from_entry,
    print_port_conflict_at_end,
)


MERGED_SAMPLE = """
services:
  proxy:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
  database:
    image: mysql:8
    ports:
      - "127.0.0.1:3307:3306"
      - target: 9000
        published: 9000
"""


class HostPortParseTest(unittest.TestCase):

    def test_parse_short_mapping(self):
        self.assertEqual(80, parse_host_port_from_entry("80:80"))

    def test_parse_ip_mapping(self):
        self.assertEqual(3307, parse_host_port_from_entry("127.0.0.1:3307:3306"))

    def test_parse_long_syntax(self):
        self.assertEqual(9000, parse_host_port_from_entry({"target": 9000, "published": 9000}))

    def test_parse_env_resolved_value(self):
        self.assertEqual(3307, parse_host_port_from_entry("3307:3306"))

    def test_skip_container_only_shorthand(self):
        self.assertIsNone(parse_host_port_from_entry("80"))

    def test_skip_dynamic_publish_zero(self):
        self.assertIsNone(parse_host_port_from_entry({"target": 80, "published": 0}))

    def test_extract_from_merged_config(self):
        port_map = extract_host_ports_from_merged_config(MERGED_SAMPLE)
        self.assertEqual(["proxy"], port_map[80])
        self.assertEqual(["proxy"], port_map[443])
        self.assertEqual(["database"], port_map[3307])
        self.assertEqual(["database"], port_map[9000])

    def test_find_duplicate_host_ports(self):
        port_map = {80: ["proxy", "frontend"]}
        lines = find_duplicate_host_ports(port_map)
        self.assertEqual(1, len(lines))
        self.assertIn("80", lines[0])
        self.assertIn("proxy", lines[0])
        self.assertIn("frontend", lines[0])


class HostPortCheckerRunTest(unittest.TestCase):

    def test_passes_when_ports_free(self):
        checker = HostPortChecker("demo", "default", MERGED_SAMPLE)
        with mock.patch("poco.services.host_port_checker.docker_check_available", return_value=True):
            with mock.patch("poco.services.host_port_checker.socket_tool_name", return_value="ss"):
                with mock.patch("poco.services.host_port_checker.query_docker_publishers", return_value=[]):
                    with mock.patch(
                        "poco.services.host_port_checker.is_port_listening_via_socket",
                        return_value=(False, None),
                    ):
                        result = checker.run()
        self.assertIsNone(result)

    def test_ignores_own_project_containers(self):
        checker = HostPortChecker("demo", "default", "services:\n  proxy:\n    ports:\n      - '80:80'\n")
        own = [{"name": "demo-proxy-1", "project": "demo", "image": "nginx"}]
        with mock.patch("poco.services.host_port_checker.docker_check_available", return_value=True):
            with mock.patch("poco.services.host_port_checker.socket_tool_name", return_value=None):
                with mock.patch("poco.services.host_port_checker.query_docker_publishers", return_value=own):
                    result = checker.run()
        self.assertIsNone(result)

    def test_foreign_docker_publish_conflict(self):
        checker = HostPortChecker("demo", "default", "services:\n  proxy:\n    ports:\n      - '80:80'\n")
        foreign = [{"name": "other-proxy-1", "project": "other", "image": "nginx:alpine"}]
        with mock.patch("poco.services.host_port_checker.docker_check_available", return_value=True):
            with mock.patch("poco.services.host_port_checker.socket_tool_name", return_value=None):
                with mock.patch("poco.services.host_port_checker.query_docker_publishers", return_value=foreign):
                    result = checker.run()
        self.assertIsInstance(result, PortConflict)
        self.assertIn("Port 80", result.message)
        self.assertIn("other-proxy-1", result.message)
        self.assertIn("other", result.message)
        self.assertTrue(result.message.strip().endswith('(compose project "other")'))

    def test_unknown_listener_conflict(self):
        checker = HostPortChecker("demo", "default", "services:\n  proxy:\n    ports:\n      - '80:80'\n")
        with mock.patch("poco.services.host_port_checker.docker_check_available", return_value=True):
            with mock.patch("poco.services.host_port_checker.socket_tool_name", return_value="ss"):
                with mock.patch("poco.services.host_port_checker.query_docker_publishers", return_value=[]):
                    with mock.patch(
                        "poco.services.host_port_checker.is_port_listening_via_socket",
                        return_value=(True, "nginx"),
                    ):
                        result = checker.run()
        self.assertIsInstance(result, PortConflict)
        self.assertIn("unknown", result.message)
        self.assertIn("Port 80", result.message)

    def test_internal_duplicate_conflict(self):
        yaml_text = (
            "services:\n"
            "  a:\n    ports:\n      - '80:80'\n"
            "  b:\n    ports:\n      - '80:80'\n"
        )
        checker = HostPortChecker("demo", "default", yaml_text)
        result = checker.run()
        self.assertIsInstance(result, PortConflict)
        self.assertIn("Duplicate host ports", result.message)

    def test_skipped_when_no_tools(self):
        checker = HostPortChecker("demo", "default", MERGED_SAMPLE)
        with mock.patch("poco.services.host_port_checker.docker_check_available", return_value=False):
            with mock.patch("poco.services.host_port_checker.socket_tool_name", return_value=None):
                with mock.patch("poco.services.console_logger.ColorPrint.print_warning") as warning:
                    result = checker.run()
        self.assertIsNone(result)
        warning.assert_called()
        self.assertIn("skipped", warning.call_args[0][0])

    def test_skipped_when_merged_config_invalid(self):
        checker = HostPortChecker("demo", "default", ":::not yaml")
        with mock.patch("poco.services.console_logger.ColorPrint.print_warning") as warning:
            result = checker.run()
        self.assertIsNone(result)
        warning.assert_called()

    def test_no_host_ports_still_passes(self):
        checker = HostPortChecker("demo", "default", "services:\n  app:\n    image: ubuntu\n")
        result = checker.run()
        self.assertIsNone(result)


class HostPortPlatformTest(unittest.TestCase):

    def test_windows_cmd_detection(self):
        env = {"COMSPEC": r"C:\Windows\System32\cmd.exe"}
        with mock.patch.dict(os.environ, env, clear=False):
            with mock.patch("poco.services.host_port_checker.sys.platform", "win32"):
                os.environ.pop("MSYSTEM", None)
                os.environ.pop("PSModulePath", None)
                self.assertTrue(is_windows_command_prompt())

    def test_git_bash_not_cmd(self):
        env = {"COMSPEC": r"C:\Windows\System32\cmd.exe", "MSYSTEM": "MINGW64"}
        with mock.patch.dict(os.environ, env, clear=False):
            with mock.patch("poco.services.host_port_checker.sys.platform", "win32"):
                self.assertFalse(is_windows_command_prompt())


class HostPortMessageTest(unittest.TestCase):

    def test_conflict_message_structure(self):
        message = format_conflict_message(
            "karcsinator",
            "default",
            ["  Port 80:", "    container: x"],
            [],
            ['Stop the conflicting stack: poco down (compose project "other")'],
        )
        self.assertIn("Cannot start project", message)
        self.assertIn("Host port conflicts:", message)
        self.assertTrue(message.strip().endswith('(compose project "other")'))

    def test_print_port_conflict_at_end_writes_tty(self):
        conflict = PortConflict("Cannot start.\n\nHost port conflicts:\n  Port 80:\n")
        tty = StringIO()
        with mock.patch("poco.services.console_logger.ColorPrint.print_error") as print_error:
            print_port_conflict_at_end(conflict, tty_stream=tty)
        print_error.assert_called_once()
        self.assertIn("Port 80", tty.getvalue())
