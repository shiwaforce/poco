# POCOK
[![Build Status](https://travis-ci.org/shiwaforce/pocok.svg?branch=master)](https://travis-ci.org/shiwaforce/pocok)
[![pypi](https://img.shields.io/pypi/v/pocok.svg)](https://pypi.python.org/pypi/pocok)
[![pypi](https://img.shields.io/pypi/pyversions/pocok.svg)](https://pypi.python.org/pypi/pocok)
[![Test Coverage](https://api.codeclimate.com/v1/badges/62a09af060af69ece1d2/test_coverage)](https://codeclimate.com/github/shiwaforce/pocok/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/62a09af060af69ece1d2/maintainability)](https://codeclimate.com/github/shiwaforce/pocok/maintainability)

<p align="center">
  <img width="200" height="200" title="Pocok Logo" src="https://raw.githubusercontent.com/shiwaforce/pocok/master/logo.svg?sanitize=true"/>
</p>

**Pocok** helps to organise and manage Docker, Docker-Compose, Kubernetes projects of any complexity using simple YAML config files to shorten the route from finding your project to initialising it in your local environment. 

- **Simple**. Configure, run and switch between projects with a very simple command line interface.     
- **Flexibility**. Manage, scale, maintain projects of any complexity with ease.
- **Configure Once, Use Everywhere**. Configure project once so the rest of your team will feel the value of zero configuration. 

## Features
- **Docker, Docker-Compose, Kubernetes, Helm** support out of the box.
- **Git, SVN** support out of the box.
- **Project Catalog, Multiple Catalogues**. Create your own project catalog. Organise and your projects without additional tools.
- **Multiple Plans**. Create multiple plans for different environments or even environments for demo purposes. Switch between plans (environments) with ease.
- **Simple Config Files**. Pocok helps to split config files, so it is easy to maintain and scale them any time.
- **Script Support (Hooks)**. Add additional scripts any time.


## Documentation
All documentation is available on [pocok.io](https://pocok.io)
- [Documentation](http://pocok.io/documentation) 
- [Overview](http://pocok.io/documentation/) 
- [Tutorials](http://pocok.io/tutorials/) 
- [Github, Gitlab Integration](http://pocok.io/documentation/third-party-integrations/) 


## Requirements
- Git or SVN
- SSH
- Docker (17.0.0 or higher version is recommended)
- kubectl, for Kubernetes support
- helm, for helm functionality support

## Quick start
Install `pocok`:
```
$:~ pip install pocok
```

Init project:
```
$:~ mkdir my-project
$:~ cd my-project
$:~ pocok init
```
`pocok.yml` and `docker-compose.yml` example files will be created.

Start project:
```
$:~ pocok up
```

Before adding your project to Pocok Repo create new empty git repository,
add repository to your local Pocok Repo config:
```
$:~ pocok repo add <name> <git-url>
```

Now you can add you project to repo:
```
$:~ pocok project add [<target-dir>] [<catalog>]
```

Publish your changes:
```
$:~ pocok repo push
```

Stop your project:
```
$:~ pocok stop
```

## Licence
[MIT](http://opensource.org/licenses/MIT)
Copyright (c) 2017-present, [Shiwaforce.com](https://www.shiwaforce.com)
