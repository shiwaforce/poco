Project Compose
===============

.. image:: https://travis-ci.org/shiwaforce/project-compose.svg?branch=master
    :target: https://travis-ci.org/shiwaforce/project-compose

.. image:: https://img.shields.io/pypi/v/project-compose.svg
    :target: https://pypi.python.org/pypi/project-compose

About
-----

Project Compose lets you catalogue and manage your Docker projects using simple YAML files to shorten the route from finding your project to initialising it in your local environment.

This helps you set up your local development environment and to run demos.

Working examples can be found here: https://github.com/shiwaforce/project-compose-example

Requirements
------------

 - Docker, version > 17
 - Python, version > 2.7

Quick start
===========

[![asciicast](https://asciinema.org/a/131956.png)](https://asciinema.org/a/131956)

Install the latest project-compose and initialise the sample catalogue:

``$ pip install project-compose``

``$ project-catalog init https://github.com/shiwaforce/project-compose-example.git``

List all projects in the catalogue and list all available modes of the example-voting-app:

``$ project-catalog ls``

``example-voting-app``

``$ project-compose mode ls example-voting-app``

``default``

``javaworker``

``simple``

Make sure your local Docker engine is up and running.

Start the Docker example voting app in javaworker mode:

``$ project-compose start example-voting-app javaworker``

This will download all the required Docker images and start them. The last step of the process will issue a "docker ps" command listing all the running containers.

Visit http://localhost:5000 to see the application's main page.

The application was started in javaworker mode, so the examplevotingapp_worker container contains OpenJDK 1.8 to run the worker node.

Stop the example voting app:

``$ project-compose down example-voting-app javaworker``

``Project stopped``

Start the Docker example voting app in default mode:

``$ project-compose start example-voting-app default``

Visit http://localhost:5000 to see the application's main page.

The application was started in default mode, so the examplevotingapp_worker container runs .Net in the worker node.

Stop the example voting app:

``$ project-compose down example-voting-app default``

``Project stopped``

Custom installation and configuration
=====================================

To be added later.

Detailed installation steps
---------------------------

Use pip:

``$ pip install project-compose``

or

``$ python setup.py install``

Home directory
--------------

The home directory must exist in the user's local home directory with the name: .project-compose

For example (OSX):
    /Users/john.doe/.project-compose

Basic configuration file
------------------------

Location: under the home directory with name: config
The format of the file is YAML, including a default section.

If the default section is empty the project-catalog.yml file must exist in the config directory

Parameters:
 - repositoryType (optional):  git | svn | file
 - url (optional): must be a valid GIT or SVN url
 - file (optional): catalog file path in the repository or local filesystem - default : project-catalog.yml
 - branch (optional): branch name - default : master
 - ssh-key (optional): ssh file location for git repository - default: ~/.ssh/id_rsa
 - workspace (optional): the base directory, where the project will be checked out - default : ~/workspace

Example 1 (empty):
::

    default:

Example 2 (Git):
::

    default:
        repositoryType: git
        url: https://github.com/shiwaforce/project-compose-example.git
        file: project-catalog.yml
        branch: master

Project catalog file
--------------------

It describes the lists of the projects and the location of the projects' project-compose files in YAML format.

Configuration:
 - keys: The name of the projects
 - git (optional): must be a valid GIT url for the project
 - svn (optional): must be a valid SVN url for the project
 - branch (optional): branch name - default : master
 - file (optional): path to the project-compose file. - Default : project-compose.yml
 - repository-dir (optional): the base directory name where the project will be checked out. - Default: name of the project
 - ssh-key (optional): ssh file location for the Git repository - default: ~/.ssh/id_rsa

If you don't define the repository it will be relative to the config file's location

If the path ends with a name of a directory it will be extended with the default filename : project-compose.yml

For example:
::

    test1:
        git: https://github.com/shiwaforce/project-compose-example.git
        branch: master
    test2:
        svn: http://svn.apache.org/repos/test2/trunk
    test3:
        file: test3
    test4:
        git: ssh://git@git.example.com/test4/test4.git
        file: another/directory/anoter_compose.yml

Project-compose file
--------------------

It describes the project's hierarchy divided into several 'modes' in YAML format.

If you don't declare a section under a mode it will take the compose-files into account.

Steps defined in the before_scripts section will run before the compose command (build, config, up, start)

In the working-directory section you can change the working directory (the default is the parent
of the compose file)

Each row in the checkout section will check out a Git repository to the target directory
which is relative to the compose file or the working directory if it is set.

For example:
::

    version: '2.0'
    maintainer: "operations@shiwaforce.com"
    containers:
        sample: dc-sample.yml
        mysql: dc-mysql.yml
    before_script:
        - ls -l
    after_script:
        - ls -l
    checkout: bankarmulato ssh://git@git.shiwaforce.com:7999/teszt/teszt.git
    working-directory: microservice-all-war
    enviroment:
        include: conf/default.env
    mode:
        demo:
            enviroment:
                include: conf/dev/dev.env
                external: svn
            docker-compose-file: sample
        dev/sw: sample
        dev/default:
            - docker-compose.yml
        dev/java: docker-compose.yml
        dev/js:
            enviroment:
                include: conf/dev/dev.env
            docker-compose-file:
                  - docker-compose.yml
                  - docker-compose.yml

Commands
--------

    **project-catalog add [<target-dir>]**

adds the current directory (or target directory) to the project-catalog (if it is a Git repository)

    **project-catalog ls**

lists the available projects (from the project catalog file)

    **project-catalog config**

prints the local config

    **project-catalog init [<repository-url>] [<repository-type>] [<file>]**

creates the config and project-catalog files if they do not exist. if the repository-url, type, and file references are not empty it will write to the local config

    **project-catalog branch <branch> [-f]**

switches branch in the project-catalog repository, use -f to force

    **project-catalog branches**

lists the available project-catalog repository branches

    **project-catalog push**

pushes project-catalog changes to the repository (if it is not a local file)

    **project-catalog remove <project>**

removes selected project form the project-catalog

    **project-compose config <project> [mode]**

prints the full config for selected project with mode (docker-compose file with environment variables)

    **project-compose clean**

cleans up all docker images, volumes and pulled repositories and data

    **project-compose init <project>**

initialises selected project with the following steps:
creates the project-compose file if it does not exist
creates the docker-compose sample file if it does not exist

    **project-compose install <project> [mode]**

installs selected project with selected mode
gets project descriptors from repository

    **project-compose up <project> [mode]**

starts the project with selected mode (if exists)
installs if it isn't installed yet

    **project-compose down <project> [mode]**

stops docker containers belonging the given project with selected mode

    **project-compose build <project> [mode]**

builds docker images for the selected project with the specified mode

    **project-compose ps <project> [mode]**

lists the state of docker images in selected project

    **project-compose mode ls <project>**

lists available modes in selected projects

    **project-compose pull <project> [mode]**

pulls docker images for the specified project with the selected mode

    **project-compose start <project> [mode]**

alternative for up

    **project-compose stop <project> [mode]**

stops docker containers which belongs to the specified project with selected mode

    **project-compose log <project> [mode]**

prints log from docker containers which belongs to the specified project with selected mode

    **project-compose logs <project> [mode]**

prints log from docker containers which belongs to the specified project with selected mode

    **project-compose branch <project> <branch>**

switches branch in the specified project repository

    **project-compose branches <project>**

lists the available project-catalog repository branches

    **project-service start <project>**

starts docker containers which belong to the selected project

    **project-service stop <project>**

stops docker containers which belong to the selected project

    **project-service restart <project>**

restarts docker containers which belong to the selected project

Local uninstall
---------------

Delete the egg file from the current Python site-packages (for example: sf_project_compose-0.3-py2.7)

OSX
"""
remove scripts from /usr/local/bin (project-catalog, project-compose, project-servive)

License
-------

MIT

Contributors
------------

`ShiwaForce.com Inc.  <https://www.shiwaforce.com/en/>`_
