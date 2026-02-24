# POCO

[![Test](https://github.com/shiwaforce/poco/actions/workflows/test.yaml/badge.svg)](https://github.com/shiwaforce/poco/actions/workflows/test.yaml)
[![pypi](https://img.shields.io/pypi/v/poco.svg)](https://pypi.python.org/pypi/poco)
[![pypi](https://img.shields.io/pypi/pyversions/poco.svg)](https://pypi.python.org/pypi/poco)
[![Test Coverage](https://api.codeclimate.com/v1/badges/62a09af060af69ece1d2/test_coverage)](https://codeclimate.com/github/shiwaforce/poco/test_coverage)
[![Maintainability](https://api.codeclimate.com/v1/badges/62a09af060af69ece1d2/maintainability)](https://codeclimate.com/github/shiwaforce/poco/maintainability)

<p align="center">
  <img width="200" height="200" title="Poco Logo" src="https://raw.githubusercontent.com/shiwaforce/poco/master/logo.svg?sanitize=true"/>
</p>

**Poco** is one CLI for **Docker**, **Kubernetes** and **Helm**: catalogue and run compose projects, switch kubectl context and namespace, and list Helm repos and releases — without leaving your terminal or remembering three different tools.

- **Docker** — `poco up`, `poco down`, `poco ps`, `poco status` (overview), compose config, build, pull; YAML catalog and plans.
- **Kubernetes** — `poco kubectx`, `poco kubens` (list/switch context and namespace); `poco kube-get pods|ns|svc|...`; presets (context+namespace in one command).
- **Helm** — `poco helm-repos`, `poco helm-list` (releases; optional `--all-namespaces`, `-i` to pick and show status).

- **Simple**. Configure, run and switch between projects with a very simple command line interface.
- **Flexibility**. Manage, scale, maintain projects of any complexity with ease.
- **Configure Once, Use Everywhere**. Configure project once so the rest of your team will feel the value of zero configuration.

## Features

- **Docker, Kubernetes, Helm in one place** — Compose projects, kubectl context/namespace, Helm repos and releases.
- **Git, SVN** support out of the box.
- **Project Catalog, Multiple Catalogues**. Create your own project catalog. Organise your projects without additional tools.
- **Multiple Plans**. Create multiple plans for different environments or even environments for demo purposes. Switch between plans (environments) with ease.
- **Simple Config Files**. Poco helps to split config files, so it is easy to maintain and scale them any time.
- **Script Support (Hooks)**. Add additional scripts any time.

## Global options

- `-i`, `--interactive` — Interactive menu: choose actions step by step without typing commands (`poco -i`).
- `-V`, `--verbose` — Print more (e.g. merged docker compose config for `up`/`down`).
- `-VV` or `--no-matrix` — No matrix effect, show full output (for `up`/`down`). Implies verbose.
- `-q`, `--quiet` — Print less.
- `--offline` — Offline mode.
- `--always-update` — Project repository handle by user.

For `poco up` / `poco down`, a matrix-style effect runs by default; only the final result is shown. Set `POCO_MATRIX=0` to disable the effect, or use `-VV` / `--no-matrix` to disable it and see the full log.

## Documentation

All documentation is available on [getpoco.io](https://getpoco.io/)

- [Documentation](https://getpoco.io/documentation/)
- [Install](https://getpoco.io/documentation/install/)
- [Tutorials](https://getpoco.io/tutorials/hello-world/)
- [Github, Gitlab Integration](https://getpoco.io/documentation/third-party-integrations/)

## Requirements

- **Python 3.12.3** or newer (supported version: **3.14.3**)
- Git or SVN
- SSH
- Docker (17.0.0 or higher version is recommended)
- Docker Compose V2 (plugin: `docker compose`), for compose support
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

Now you can add your project to repo:

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

## One CLI: Docker, kubectl, Helm

| Stack    | Poco commands | What you get |
|----------|----------------|--------------|
| **Docker** | `poco up`, `poco down`, `poco ps`, `poco config`, … | Compose projects from a YAML catalog; matrix-style run; verbose merged config. |
| **Kubernetes** | `poco kubectx`, `poco kubens` | List/switch context and namespace (kubectx/kubens-style). |
| **Helm** | `poco helm-repos`, `poco helm-list` | List repos and releases; `helm-list --all-namespaces` for all. |

Requires Docker and/or `kubectl`/`helm` installed. Poco checks availability and works with different kubectl/helm versions.

### Presets (workflow)

Save and switch context + namespace in one step:

- `poco preset list` — List saved presets.
- `poco preset use <name>` — Switch to a preset (context and namespace).
- `poco preset save <name>` — Save current context and namespace as a preset.

Presets are stored in `~/.poco/presets.yml`.

### Kube-get

Shortcut for common `kubectl get` usage:

- `poco kube-get <resource> [name]` — e.g. `poco kube-get pods`, `poco kube-get ns`, `poco kube-get svc`.
- Use `-n <namespace>` or `-A` (all namespaces) when needed.

### Interactive mode (`-i` / `--choose`)

When a command can show a list, use `-i` to pick from a menu (or fzf if installed):

- `poco kubectx -i` — Choose context from list.
- `poco kubens -i` — Choose namespace from list.
- `poco preset use -i` — Choose preset from list.
- `poco helm-list -i` — Choose release, then show `helm status`.

## Security

- **Dependencies:** We track known vulnerabilities and bump affected packages (e.g. GitPython ≥3.1.41 for CVE fixes). To audit your install: `pip install pip-audit && pip-audit` (or `pip-audit -r requirements.txt`).
- **Build tools:** Keep setuptools and wheel up to date: `pip install -U setuptools wheel` to address CVEs in the toolchain.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for release history. **1.0** — Docker + Kubernetes + Helm in one CLI; presets; kube-get; interactive menu (`poco -i`); `poco status`; matrix effect; before_docker_script; security (GitPython, pip-audit).

## Licence

[MIT](http://opensource.org/licenses/MIT)
Copyright (c) 2017-present, [Shiwaforce.com](https://www.shiwaforce.com/en/)
