# POCO
[![Build Status](https://travis-ci.org/shiwaforce/poco.svg?branch=command-refactor)](https://travis-ci.org/shiwaforce/poco)
[![pypi](https://img.shields.io/pypi/v/poco.svg)](https://pypi.python.org/pypi/poco)
[![python](https://img.shields.io/pypi/pyversions/poco.svg)](https://pypi.python.org/pypi/poco)

<img src="https://raw.githubusercontent.com/shiwaforce/poco/command-refactor/logo.jpg" align="center" width="140" height="140" style="display:block; margin: 0 auto;">
`poco` is a docker-compose missing tool. With it's help you will be able to manage docker projects of the any complexity with ease.
It is just indispensable tool for the projects with few or more environments.
You can use `poco` for development and for demo purposes as well.
Kubernetes is also supported.

## Requirements
- Docker, version > 17, if you want use Docker-compose files
- kubectl, if you want use Kubernetes


## Getting started
#### Install `poco`:
```
$ pip install poco
```

#### Create `poco` project:
```
$ mkdir poco-project
$ cd poco-project
$ poco init
```
`poco.yml` and `docker-compose.yml` example files will be created.

#### Start `poco` project:
```
$ poco start
```

#### Create `poco repo`:
```
$ poco repo init
```
Sample catalog will be initialised with the default environment

#### Add remote catalog
```
$ poco repo add <name> <git-ssh-url> [<branc>] [<file>]
```

#### Add `poco` project into catalog:
```
$ poco project add [<target-dir>] [<catalog>]
```

#### Publish (push) `poco repo`:
```
$ poco repo push
```


## Terminology 
`poco` - 
`poco repo` - 
`poco project` - 
`plan`


## Commands
### `poco`
| Command                                            | Parameters | Description |
|----------------------------------------------------|------------|-------------|
| `poco project-config [<project>] [<plan>]`         |            |             |

### `poco repo`
### `poco project`