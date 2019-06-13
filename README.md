# POCO

[![Build Status](https://travis-ci.org/shiwaforce/poco.svg?branch=master)](https://travis-ci.org/shiwaforce/poco)
[![pypi](https://img.shields.io/pypi/v/poco.svg)](https://pypi.python.org/pypi/poco)
[![pypi](https://img.shields.io/pypi/pyversions/poco.svg)](https://pypi.python.org/pypi/poco)
[![Test Coverage](https://api.codeclimate.com/v1/badges/62a09af060af69ece1d2/test_coverage)](https://codeclimate.com/github/shiwaforce/poco/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/62a09af060af69ece1d2/maintainability)](https://codeclimate.com/github/shiwaforce/poco/maintainability)

<p align="center">
  <img width="200" height="200" title="Poco Logo" src="https://raw.githubusercontent.com/shiwaforce/poco/master/logo.svg?sanitize=true"/>
</p>

**Poco** helps to organise and manage Docker, Docker-Compose, Kubernetes projects of any complexity using simple YAML config files to shorten the route from finding your project to initialising it in your local environment.

- **Simple**. Configure, run and switch between projects with a very simple command line interface.
- **Flexibility**. Manage, scale, maintain projects of any complexity with ease.
- **Configure Once, Use Everywhere**. Configure project once so the rest of your team will feel the value of zero configuration.

## Features

- **Docker, Docker-Compose, Kubernetes, Helm** support out of the box.
- **Git, SVN** support out of the box.
- **Project Catalog, Multiple Catalogues**. Create your own project catalog. Organise and your projects without additional tools.
- **Multiple Plans**. Create multiple plans for different environments or even environments for demo purposes. Switch between plans (environments) with ease.
- **Simple Config Files**. Poco helps to split config files, so it is easy to maintain and scale them any time.
- **Script Support (Hooks)**. Add additional scripts any time.

## Documentation

All documentation is available on [getpoco.io](https://getpoco.io/)

- [Documentation](https://getpoco.io/documentation/)
- [Install](https://getpoco.io/documentation/install/)
- [Tutorials](https://getpoco.io/tutorials/hello-world/)
- [Github, Gitlab Integration](https://getpoco.io/documentation/third-party-integrations/)

## Requirements

- Git or SVN
- SSH
- Docker (17.0.0 or higher version is recommended)
- kubectl, for Kubernetes support
- helm, for helm functionality support

## Quick start

Install `poco`:

```
$:~ pip install poco
```

Init project:

```
$:~ mkdir my-project
$:~ cd my-project
$:~ poco init
```

`poco.yml` and `docker-compose.yml` example files will be created.

Start project:

```
$:~ poco up
```

Before adding your project to Poco Repo create new empty git repository,
add repository to your local Poco Repo config:

```
$:~ poco repo add <name> <git-url>
```

Now you can add you project to repo:

```
$:~ poco project add [<target-dir>] [<catalog>]
```

Publish your changes:

```
$:~ poco repo push
```

Stop your project:

```
$:~ poco stop
```

## Licence

[MIT](http://opensource.org/licenses/MIT)
Copyright (c) 2017-present, [Shiwaforce.com](https://www.shiwaforce.com/en/)
