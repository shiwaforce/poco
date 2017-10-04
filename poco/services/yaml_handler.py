from .console_logger import ColorPrint
import yaml


class YamlHandler:

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
