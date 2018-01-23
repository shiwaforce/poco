import os


class StateHolder:

    home_dir = None
    container_mode = "Docker"
    catalog_config_file = None
    global_config_file = None
    base_work_dir = os.path.join(os.path.expanduser(path='~'), 'workspace')
    work_dir = None
    config_parsed = False

    '''input arguments'''
    args = dict()

    ''' full content of catalogue's config file'''
    config = None

    ''' full contents of catalog files '''
    catalogs = None

    ''' content of requested catalog '''
    catalog_element = None

    '''project name'''
    name = None

    plan = None

    mode = None

    ''' submodes '''
    offline = False
    always_update = True

    '''For not Docker mode'''
    skip_docker = False

    ''' handlers '''
    config_handler = None
    compose_handler = None
    catalog_handler = None

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
