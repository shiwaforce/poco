"""Unit tests for before_docker_script: get_before_docker_script_commands and OS merging."""
import platform
from unittest import mock

from poco.services.compose_handler import ComposeHandler


def test_get_before_docker_script_commands_returns_linux_commands():
    handler = ComposeHandler.__new__(ComposeHandler)
    handler.compose_project = {
        "plan": {"default": {}},
        "before_docker_script": {
            "linux": ["mkdir -p ./data", "chmod +x ./scripts/*.sh"],
            "windows": ["mkdir .\\data"],
        },
    }
    handler.plan = "default"
    with mock.patch.object(platform, "system", return_value="Linux"):
        out = handler.get_before_docker_script_commands(handler.compose_project["plan"]["default"])
    assert out == ["mkdir -p ./data", "chmod +x ./scripts/*.sh"]


def test_get_before_docker_script_commands_returns_windows_commands():
    handler = ComposeHandler.__new__(ComposeHandler)
    handler.compose_project = {
        "plan": {"default": {}},
        "before_docker_script": {
            "linux": ["mkdir -p ./data"],
            "windows": ["if not exist .\\data mkdir .\\data"],
        },
    }
    handler.plan = "default"
    with mock.patch.object(platform, "system", return_value="Windows"):
        out = handler.get_before_docker_script_commands(handler.compose_project["plan"]["default"])
    assert out == ["if not exist .\\data mkdir .\\data"]


def test_get_before_docker_script_commands_plan_overrides_project():
    handler = ComposeHandler.__new__(ComposeHandler)
    handler.compose_project = {
        "plan": {"default": {}},
        "before_docker_script": {
            "linux": ["project_cmd"],
        },
    }
    handler.plan = "default"
    plan = {"before_docker_script": {"linux": ["plan_cmd"]}}
    with mock.patch.object(platform, "system", return_value="Linux"):
        out = handler.get_before_docker_script_commands(plan)
    assert out == ["plan_cmd"]


def test_get_before_docker_script_commands_empty_when_os_missing():
    handler = ComposeHandler.__new__(ComposeHandler)
    handler.compose_project = {
        "plan": {"default": {}},
        "before_docker_script": {"linux": ["mkdir -p ./data"]},
    }
    handler.plan = "default"
    with mock.patch.object(platform, "system", return_value="Windows"):
        out = handler.get_before_docker_script_commands(handler.compose_project["plan"]["default"])
    assert out == []


def test_get_before_docker_script_commands_empty_when_block_missing():
    handler = ComposeHandler.__new__(ComposeHandler)
    handler.compose_project = {"plan": {"default": {}}}
    handler.plan = "default"
    with mock.patch.object(platform, "system", return_value="Linux"):
        out = handler.get_before_docker_script_commands(handler.compose_project["plan"]["default"])
    assert out == []


def test_get_before_docker_script_commands_mac_alias_for_darwin():
    handler = ComposeHandler.__new__(ComposeHandler)
    handler.compose_project = {
        "plan": {"default": {}},
        "before_docker_script": {"mac": ["mkdir -p ./data"]},
    }
    handler.plan = "default"
    with mock.patch.object(platform, "system", return_value="Darwin"):
        out = handler.get_before_docker_script_commands(handler.compose_project["plan"]["default"])
    assert out == ["mkdir -p ./data"]


def test_get_before_docker_script_commands_single_string_normalized_to_list():
    handler = ComposeHandler.__new__(ComposeHandler)
    handler.compose_project = {
        "plan": {"default": {}},
        "before_docker_script": {"linux": "single_cmd"},
    }
    handler.plan = "default"
    with mock.patch.object(platform, "system", return_value="Linux"):
        out = handler.get_before_docker_script_commands(handler.compose_project["plan"]["default"])
    assert out == ["single_cmd"]
