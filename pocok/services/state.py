import os


class StateHolder:

    # Globals
    home_dir = None
    catalog_config_file = None
    global_config_file = None
    repositories = dict()

    # input arguments
    args = dict()

    # Working directory
    base_work_dir = os.path.join(os.path.expanduser(path='~'), 'workspace')
    work_dir = None

    # Config section
    config_parsed = False
    config = None  # full content of catalogue's config file

    # Catalog section
    catalogs = None  # full contents of catalog files
    catalog_element = None  # content of requested catalog

    # Mode and mode properties
    mode = None
    mode_properties = ['offline', 'always_update']  # TODO maybe more dynamic
    offline = False
    always_update = True

    # Project properties
    name = None
    plan = None
    repository = None

    poco_file = None

    # Virtualization type
    container_mode = "Docker"
    test_mode = False  # Not running scrips and virtualization types

    # Handlers
    compose_handler = None

    # Catalog repositories
    catalog_repositories = dict()
    default_catalog_repository = None

    @staticmethod
    def has_args(*args):
        for arg in args:
            if not StateHolder.args.get(arg):
                return False
        return True

    @staticmethod
    def has_least_one_arg(*args):
        for arg in args:
            if StateHolder.args.get(arg):
                return True
        return False

    @staticmethod
    def process_extra_args():
        for prop in StateHolder.mode_properties:
            param_name = "--" + prop.replace("_", "-")
            val = StateHolder.args.get(param_name)
            if val:
                setattr(StateHolder, prop, val)
