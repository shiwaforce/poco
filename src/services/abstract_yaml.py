from .console_logger import ColorPrint
import yaml


class AbstractYamlHandler(object):

    def __init__(self, file):
        self.file = file
        self.parsed = False

    def read(self, doc=None):
        with open(self.file) as stream:
            try:
                content = yaml.load(stream=stream)
                if content is None:
                    ColorPrint.exit_after_print_messages(message="Error: Wrong YAML format", doc=doc)
                self.parsed = True
                return content
            except yaml.YAMLError as exc:
                ColorPrint.exit_after_print_messages(message="Error: Wrong YAML format:\n" + str(exc), doc=doc)

    def write(self, data):
        with open(self.file, 'w') as stream:
            stream.write(yaml.dump(data=data, default_flow_style=False))

    def get_file(self):
        return self.file
