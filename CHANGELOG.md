# Changelog

All notable changes to poco are documented here.

## [0.99.9.5] - 2026-02-25

### Fixed

- **Windows matrix on `poco up`** — Redirect our own stdout/stderr to the pipe so messages like "Executing before_script" and "Docker command" no longer add extra static lines; only the 20-line matrix moves, same as `poco down`.

## [0.99.9.4] - 2026-02-25

### Fixed

- **Windows `poco up` + matrix** — Matrix no longer runs forever: subprocess output is now read in a background thread so the pipe buffer never fills and the process can finish (avoids deadlock when docker compose writes a lot).

## [0.99.9.3] - 2026-02-25

### Fixed

- **Matrix on Windows** — Subprocess output (e.g. docker compose) is now captured via pipe so it no longer flashes through during the matrix; only the final result block is shown. No dup2 (avoids OSError 22).

### Changed

- **Matrix effect** — Smoother on Windows: longer refresh interval (0.05s) and explicit flush; avoids choppy display on CON/console.

## [0.99.9.2] - 2026-02-25

### Security

- **GitPython** — Bumped from 3.1.30 to 3.1.41 to address PYSEC-2024-4, PYSEC-2023-137, PYSEC-2023-161, PYSEC-2023-165 (Windows path, clone options, path traversal). Run `pip-audit -r requirements.txt` to verify; no known vulnerabilities in declared dependencies.
- **README** — Added Security section: recommend `pip-audit` and `pip install -U setuptools wheel` for the toolchain.

### Changed

- Pytest: filter DeprecationWarnings (e.g. from PyGithub) so test runs are warning-clean.
- CI: upgrade setuptools and wheel before install; run `pip-audit` and fail on vulnerabilities.

## [0.99.9.1] - 2026-02-25

### Fixed

- **Matrix on Windows** — Avoid `OSError (22, 'Incorrect function')` by not using pipe/dup2 on Windows; matrix runs to CON while command output goes to real stdout/stderr (no capture on win32).

## [0.99.9] - 2026-02-25

### Fixed

- **Matrix effect on Windows / Git Bash** — TTY stream is now obtained via `CON` on Windows and `/dev/tty` on Unix/Git Bash so the matrix rain works in Git Bash and native Windows console.

### Changed

- Added unit tests for `_get_tty_stream` (never raise, Unix path, all fail, Windows CON).

## [0.99.8] - 2026-02-25

### Improved

- **Interactive menu (`poco -i`)** — Shows current Kubernetes context and namespace at the top when kubectl is available, so you always know where you are.

## [0.99.7] - 2026-02-17

### Added

- **Presets** — Save and switch kubectl context + namespace in one command: `poco preset list`, `poco preset use <name>`, `poco preset save <name>`. Config: `~/.poco/presets.yml`.
- **kube-get** — Shortcut for `kubectl get`: `poco kube-get <resource> [name]` with optional `-n <namespace>` and `-A` (all namespaces). E.g. `poco kube-get pods`, `poco kube-get ns`.
- **Interactive mode (`-i` / `--choose`)** — Choose from list via menu or fzf (if installed): `poco kubectx -i`, `poco kubens -i`, `poco preset use -i`, `poco helm-list -i` (pick release then show helm status).
- **Interactive menu (`poco -i`)** — Step-by-step menu: start/stop project, Kubernetes (kubectx, kubens, kube-get, preset), Helm, catalog. Colored, multi-column lists; stays in menu when a command has nothing to show.

### Changed

- Help and README: Presets, Kube-get, and Interactive mode sections; updated Kubernetes/Helm intro.

## [0.99.6] - 2026-02-24

### Added

- **kubectx** — List or switch kubectl context: `poco kubectx`, `poco kubectx <context>`.
- **kubens** — List or switch namespace: `poco kubens`, `poco kubens <namespace>`.
- **helm-repos** — List Helm repositories: `poco helm-repos`.
- **helm-list** — List Helm releases: `poco helm-list`, `poco helm-list --all-namespaces`.

### Changed

- Matrix effect: fixed height 20 lines, in-place update (no terminal scroll); width adapts to terminal (TTY fd); full-width lines, no half-filled rows.
- Verbose (`-V`): merged docker compose config shown for `up`/`down` (before result or in final block).
- `-VV` / `--no-matrix`: no matrix, full log; implies verbose.
- Help and docs: global options, Start/Stop descriptions, README Kubernetes & Helm section.

### Fixed

- `poco up -V` and `poco -VV up` now work (global options passed to subcommands; `-VV` preprocessed to `--no-matrix`).
- Subcommand help (e.g. `poco repo`) uses correct argv so help text is shown.

---

## [0.99.5] - 2026-02-23

- Matrix-style effect for `poco up` / `poco down` (optional, `POCO_MATRIX=0` to disable).
- Capture output; show only final result block (e.g. `[+] up 10/10`, container table).
- On failure: red "glitch in the matrix" on TTY + full debug log.
- CI: Code Climate coverage upload non-blocking so PyPI publish always runs.
