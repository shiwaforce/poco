

class StateHolder:

    home_dir = None
    config_file = None
    work_dir = None
    config_parsed = False

    ''' full content of config file without work_dir and developer-mode'''
    config = None

    '''project name'''
    name = None

    offline = False
    developer_mode = False

    '''For testing'''
    skip_docker = False
