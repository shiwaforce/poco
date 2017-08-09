import sys


class Colors:
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    OKBLUE = '\033[94m'
    END = '\033[0m'


class Doc:
    CONFIG = """Configuration:

    For generate default environment, please run:
        project-catalog init

    YAML format.
    Need to be an default section (it's the only one, which supported now)

    If default section is empty, the project-catalog.yml file must be exists in config directory

    repositoryType (optional):  git | svn | file
    url (optional): must be a valid GIT or SVN url
    file (optional):    catalog file path in the repository or local filesystem - default : project-catalog.yml
    branch (optional):  branch name - default : master
    ssh-key (optional): ssh file location for git repository - default: ~/.ssh/id_rsa
    workspace (optional): the directory where the script will checkout the projects - default: ~/workspace

    For example:

        default:
            repositoryType: git
            url: ssh://git@git.shiwaforce.com/scm/project-catalog/project-catalog.git
            file: project-catalog.yml
            branch: master
    """

    PROJECT_CATALOG = """Project catalog.

        YAML format.

        Generate a sample project-compose file for project, please run:
            project-compose init

        Configuration:
            keys: The name of the projects

            git (optional): must be a valid GIT url for the project
            svn (optional): must be a valid SVN url for the project
            branch (optional): branch name - default : master
            file(optional): path to the project-compose file. - Default : project-compose.yml
                If you not define repository, it will relative to config file
                If the path is a directory, then will extended the path the default filename : project-compose.yml

        For example:

          test1:
            git: ssh://git@git.example.com/test/test1.git
            branch: master
          test2:
            svn: http://svn.apache.org/repos/test2/trunk
          test3:
            file: test3
          test4:
            git: ssh://git@git.example.com/test4/test4.git
            file: another/directory/anoter_compose.yml
        """

    PROJECT_COMPOSE = """Project compose.

        YAML format.

        For example:

            version: '2.0'
            stage: GSE
            maintainer: "operation@shiwaforce.com"
            containers:
                sample: dc-sample.yml
                mysql: dc-mysql.yml
            enviroment:
                include: conf/default.env
            plan:
                default:
                    enviroment:
                        include:
                            - conf/dev/dev.env
                            - conf/dev/static.env
                    docker-compose-file:
                        - dc-app.yml
                        - sample
                        - mysql
                swdev:
                    enviroment:
                        include: conf/dev/dev.env
                    docker-compose-file:
                        - dc-app-ambassador-integtest.yml
                        - sample
                        - mysql
        """

    COMPOSE_DOC = """
            This must an docker compose file.
            URL: https://docs.docker.com/compose/

            For example:
                version: '2'
                services:
                  web:
                    build: .
                    ports:
                     - "5000:5000"
                    volumes:
                     - .:/code
                  redis:
                    image: "redis:alpine"
            """


class ColorPrint:

    log_lvl = 0

    @staticmethod
    def print_error(message):
        print(Colors.FAIL + "\n" + message + "\n" + Colors.END)

    @staticmethod
    def print_warning(message, lvl=0):
        if ColorPrint.log_lvl >= lvl:
            print(Colors.WARNING + "\n" + message + "\n" + Colors.END)

    @staticmethod
    def print_info(message, lvl=0):
        if ColorPrint.log_lvl >= lvl:
            print(Colors.OKBLUE + "\n" + message + "\n" + Colors.END)

    @staticmethod
    def print_with_lvl(message, lvl=0):
        if ColorPrint.log_lvl >= lvl:
            print(message)

    @staticmethod
    def exit_after_print_messages(message, doc=None, msg_type="error"):
        if "error" is msg_type:
            ColorPrint.print_error(message)
        elif "warn" is msg_type:
            ColorPrint.print_warning(message)
        elif "info" is msg_type:
            ColorPrint.print_info(message)
        else:
            print(message)
        if doc is not None and ColorPrint.log_lvl > -1:
            print(doc)
        sys.exit(1)

    @staticmethod
    def set_log_level(arguments):
        if arguments.get("--verbose"):
            ColorPrint.log_lvl += 1
        if arguments.get("--quiet"):
            ColorPrint.log_lvl -= 1
