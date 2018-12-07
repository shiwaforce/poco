from .console_logger import ColorPrint
from collections import OrderedDict
import yaml


class YamlUtils:

    @staticmethod
    def read(file, doc=None):
        with open(file) as stream:
            try:
                content = yaml.load(stream=stream)
                if content is None:
                    ColorPrint.exit_after_print_messages(message="Error: Wrong YAML format", doc=doc)
                return content
            except yaml.YAMLError as exc:
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
        project_config = YamlUtils.read_without_exception(file=file)
        if project_config is None:
            return False
        if 'plan' not in project_config:
            return False
        if not isinstance(project_config['plan'], dict):
            return False
        return plan in project_config['plan']

    @staticmethod
    def read_without_exception(file):
        with open(file) as stream:
            try:
                return yaml.load(stream=stream)
            except yaml.YAMLError:
                return None

    @staticmethod
    def ordered_load(stream, Loader=yaml.Loader, object_pairs_hook=OrderedDict):
        class OrderedLoader(Loader):
            pass

        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return object_pairs_hook(loader.construct_pairs(node))

        OrderedLoader.add_constructor(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            construct_mapping)
        return yaml.load(stream, OrderedLoader)
