from .console_logger import ColorPrint
from collections import OrderedDict
import yaml


class YamlUtils:

    loader = yaml.Loader if not hasattr(yaml, 'FullLoader') else yaml.FullLoader

    @staticmethod
    def read(file, doc=None, fault_tolerant=False):
        with open(file) as stream:
            try:
                return yaml.load(stream=stream, Loader=YamlUtils.loader)
            except yaml.YAMLError as exc:
                if fault_tolerant:
                    return None
                ColorPrint.exit_after_print_messages(message="Error: Wrong YAML format:\n" + str(exc), doc=doc)

    @staticmethod
    def write(file, data):
        with open(file, 'w') as stream:
            stream.write(yaml.dump(data=data, default_flow_style=False))

    @staticmethod
    def dump(data):
        ColorPrint.print_info(message=yaml.dump(
            data=data, default_flow_style=False, default_style='', indent=4), lvl=-1)

    @staticmethod
    def check_file(file, plan):
        project_config = YamlUtils.read(file=file, fault_tolerant=True)
        if project_config is None:
            return False
        if 'plan' not in project_config:
            return False
        if not isinstance(project_config['plan'], dict):
            return False
        return plan in project_config['plan']

    @staticmethod
    def ordered_load(stream, object_pairs_hook=OrderedDict):
        class OrderedLoader(yaml.SafeLoader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return object_pairs_hook(loader.construct_pairs(node))

        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        return yaml.load(stream, OrderedLoader)
