"""Load and save kubectl context+namespace presets from ~/.poco/presets.yml."""
import os
from .state import StateHolder
from .console_logger import ColorPrint
from .yaml_utils import YamlUtils


def _presets_path():
    base = StateHolder.home_dir
    if not base:
        base = os.path.join(os.path.expanduser("~"), ".poco")
    return os.path.join(base, "presets.yml")


def load_presets():
    """Return dict of presets { name: { context: str, namespace: str } }. Empty dict if file missing."""
    path = _presets_path()
    if not os.path.exists(path):
        return {}
    data = YamlUtils.read(path, fault_tolerant=True)
    if data is None or not isinstance(data, dict):
        return {}
    presets = data.get("presets") or data
    if not isinstance(presets, dict):
        return {}
    return presets


def save_presets(presets):
    """Write presets to ~/.poco/presets.yml. presets = { name: { context, namespace } }."""
    path = _presets_path()
    base = os.path.dirname(path)
    if base and not os.path.exists(base):
        os.makedirs(base, mode=0o700)
    YamlUtils.write(path, {"presets": presets})
