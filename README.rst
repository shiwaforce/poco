Pocok
=====

.. image:: https://travis-ci.org/shiwaforce/pocok.svg?branch=master
    :target: https://travis-ci.org/shiwaforce/pocok

.. image:: https://img.shields.io/pypi/v/pocok.svg
    :target: https://pypi.python.org/pypi/pocok

.. image:: https://img.shields.io/pypi/pyversions/pocok.svg
    :target: https://pypi.python.org/pypi/pocok

.. image:: https://api.codeclimate.com/v1/badges/62a09af060af69ece1d2/test_coverage
   :target: https://codeclimate.com/github/shiwaforce/pocok/test_coverage
   :alt: Test Coverage

.. image:: https://api.codeclimate.com/v1/badges/62a09af060af69ece1d2/maintainability
   :target: https://codeclimate.com/github/shiwaforce/pocok/maintainability
   :alt: Maintainability

.. image:: logo.svg
   :height: 200px
   :width: 200px

About
-----

**pocok** lets you catalogue and manage your projects using simple YAML files to shorten the route from finding your project to initialising it in your local environment.

This helps you set up your local development environment and to run demos.

Working examples can be found here: https://github.com/shiwaforce/poco-example

Requirements
------------

 - Docker, version > 17, if you want use Docker-compose files
 - kubectl, if you want use Kubernetes files
 - helm, if you want use helm functionality

Quick start
===========

.. image:: https://asciinema.org/a/137172.png
    :target: https://asciinema.org/a/137172

Install the latest pocok:

``$ pip install pocok``

It will be initialise the sample catalogue at first time

``$ pocok repo add sample https://github.com/shiwaforce/poco-example``

List all projects in the catalogue:

``$ pocok catalog``

List all available plans of the example-voting-app:

``$ pocok plan ls example-voting-app``

``default``

``javaworker``

``simple``

Make sure your local Docker engine is up and running.

Start the Docker example voting app in javaworker plan:

``$ pocok start example-voting-app javaworker``

This will download all the required Docker images and start them. The last step of the process will issue a "docker ps" command listing all the running containers.

Visit http://localhost:5000 to see the application's main page.

The application was started in javaworker plan, so the examplevotingapp_worker container contains OpenJDK 1.8 to run the worker node.

Stop the example voting app:

``$ pocok down example-voting-app javaworker``

``Project stopped``

Start the Docker example voting app in default plan:

``$ pocok start example-voting-app default``

Visit http://localhost:5000 to see the application's main page.

The application was started in default plan, so the examplevotingapp_worker container runs .Net in the worker node.

Stop the example voting app:

``$ pocok down example-voting-app default``

``Project stopped``

Custom installation and configuration
=====================================

To be added later.

Detailed installation steps
---------------------------

Use pip:

``$ pip install pocok``

or

``$ python setup.py install``

Without configuration and catalogue
-----------------------------------

If you haven't an own home directory but your actual directory contains an pocok.yml, you can use the same commands.

The "catalog" and "catalog config" commands will not works this way.

You can change docker container's names, if you use <project> parameter.

Home directory
--------------

The home directory is in the user's local home directory with the name: .pocok

For example (OSX):
    /Users/john.doe/.pocok

Basic configuration file
------------------------

Location: under the home directory with name: config
The format of the file is YAML, including a default section.

If the default section is empty the poco-catalog.yml file looking in the config directory

Parameters:
 - repositoryType (optional):  git | svn | file
 - url (optional): must be a valid GIT or SVN url
 - file (optional): catalog file path in the repository or local filesystem - default : poco-catalog.yml
 - branch (optional): branch name - default : master
 - ssh-key (optional): ssh file location for git repository - default: ~/.ssh/id_rsa
 - workspace (optional): the base directory, where the project will be checked out - default : ~/workspace
 - developer-mode (optional): git commands not be used in workspace directory - not change branch and pull in projects

Example 1 (empty):
::

    default:

Example 2 (Git, multiple):
::

    default:
        repositoryType: git
        url: https://github.com/shiwaforce/poco-example.git
        file: poco-catalog.yml
        branch: master
    another:
        repositoryType: git
        url: https://github.com/shiwaforce/poco-example-another.git
        file: poco-catalog.yml
        branch: master
    workspace: /Users/john.doe/workspace
    developer-mode: true

Project catalog file
--------------------

It describes the lists of the projects and the location of the projects' pocok files in YAML format.

Configuration:
 - keys: The name of the projects
 - git (optional): must be a valid GIT url for the project
 - svn (optional): must be a valid SVN url for the project
 - branch (optional): branch name - default : master
 - file (optional): path to the pocok file. - Default : pocok.yml
 - repository-dir (optional): the base directory name where the project will be checked out. - Default: name of the project
 - ssh-key (optional): ssh file location for the Git repository - default: ~/.ssh/id_rsa

If you don't define the repository it will be relative to the config file's location

If the path ends with a name of a directory it will be extended with the default filename : pocok.yml

For example:
::

    test1:
        git: https://github.com/shiwaforce/poco-example.git
        branch: master
    test2:
        svn: http://svn.apache.org/repos/test2/trunk
    test3:
        file: test3
    test4:
        git: ssh://git@git.example.com/test4/test4.git
        file: another/directory/anoter_compose.yml

Poco file
---------

It describes the project's hierarchy divided into several 'plans' in YAML format.

If you don't declare a section under a plan it will take the compose-files into account.

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
    checkout: test ssh://git@git.shiwaforce.com:7999/test/test.git
    working-directory: microservice-all-war
    enviroment:
        include: conf/default.env
    plan:
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
        dev/another:
            docker-compose-dir:
                - /docker-files
        dev/kubernetes:
            kubernetes-file:
                - kubernetes-file1.yaml
                - kubernetes-file2.yaml

Commands
--------

    **pocok project add [<target-dir>] [<catalog>]**

Add directory to catalog.

    **pocok project init [<name>]**

Initialize pocok project, pocok.yml and docker-compose.yml will be created if they don't exist

    **pocok project ls**

List the available projects in repos.

    **pocok project (remove|rm) <name>**

Remove project from the catalog.

    **pocok repo (add|modify) <name> <git-url> [<branch>] [<file>]**

Add new/Modify repository to the config.

    **pocok repo branch <branch> [<name>] [-f]**

Switch catalog branch if it is using GIT.

    **pocok repo branches [<name>]**

List all available branches of catalog's GIT repository.

    **pocok repo ls**

List the configs of repos.

    **pocok repo push [<name>]**

Push changes into catalog's remote GIT repository.

    **pocok repo (remove|rm) [<name>]**

Remove repository from local config.

    **pocok branch <name> <branch> [-f]**

Switch branch on a defined project.

    **pocok branches [<name>]**

List all available git branches of the project.

    **pocok build [<project/plan>]**

Build containers depends defined project and plan.

    **pocok catalog**

List the available projects in repos.

    **pocok clean**

Clean all container and image from local Docker repository.

    **pocok config [<project/plan>]**

Print full Docker compose configuration for a project's plan.

    **pocok init [<name>]**

Initialize pocok project, pocok.yml and docker-compose.yml will be created if they don't exist

    **pocok install [<project/plan>]**

Get projects from remote repository (if its not exists locally yet) and run install scripts.

    **pocok (log|logs) [<project/plan>]**

Print docker containers logs of the current project with the default or defined plan.

    **pocok pack [<project/plan>]**

Pack the selected project's plan configuration with docker images into an archive.

    **pocok plan ls [<project>]**

Print all available plans of the project.

    **pocok ps [<project/plan>]**

Print containers statuses which depends defined project and plan.

     **pocok pull [<project/plan>]**

Pull all necessary images for the project with the defined or default plan.

    **pocok restart [<project/plan>]**

Restart project with the default or defined plan.

    **pocok (start|up) [<project/plan>]**

Start pocok project with the default or defined plan.

    **pocok (stop|down) [<project/plan>]**

Stop project with the default or defined plan.

    **pocok unpack [<name>]**

Unpack archive, install images to local repository.


Local uninstall
---------------

Delete the egg file from the current Python site-packages (for example: pocok-0.90.0-py2.7)

OSX
"""
remove script from /usr/local/bin (pocok)

License
-------

MIT

Contributors
------------

`ShiwaForce.com Inc.  <https://www.shiwaforce.com/en/>`_
