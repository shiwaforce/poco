# Changelog

All notable changes to poco are documented here.

## [1.0.2] - 2026-06-22

### Added

- **Host port preflight** - Before `poco up` and `poco restart`, poco resolves host ports from the plan's compose files (`docker compose config`) and checks for conflicts. Own project containers are ignored (safe restart / partial stack). Foreign or unknown listeners produce a clear error before containers start.
- **Graceful degrade** - If socket tools (`ss`, `lsof`, `netstat`) or merged config are unavailable (e.g. Windows CMD), poco warns and continues startup instead of blocking.

### Security

- **GitPython** - Bumped from 3.1.41 to 3.1.50 (CVE-2026-42215, CVE-2026-42284, CVE-2026-44244, GHSA-mv93-w799-cj2w).

## [1.0.1] - 2026-02-28

### Added

- **Auto-create poco.yml** — When running `poco up` or `poco down` in a directory with `docker-compose.yml` (or `docker-compose.yaml`) but no `poco.yml`, poco automatically creates `poco.yml` from the existing compose file(s). No manual edit needed.
- **Docker folder support** — Auto-create also discovers compose files in a `docker/` subfolder. When root compose exists, `docker/*.yml` are added; `docker/docker-compose.yml` is skipped (avoids build context issues when app/Dockerfile are in project root).

### Changed

- **Matrix effect** — "SHIWAFORCE" occasionally readable in the falling digits during `poco up`/`poco down` (~0.8% of lines).

## [1.0] - 2026-02-25

First stable 1.0 release.

### Summary since 0.99.3

- **Kubernetes & Helm** — `kubectx`, `kubens`, `helm-repos`, `helm-list`; matrix effect and verbose for up/down; `-VV`/`--no-matrix` for full log.
- **0.99.5–0.99.6** — Matrix effect (20 lines, in-place); verbose merged compose; kubectx/kubens/helm-repos/helm-list.
- **0.99.7** — Presets (list/use/save); kube-get; interactive `-i` for kubectx/kubens/preset/helm-list; interactive menu `poco -i`.
- **0.99.8** — Interactive menu shows current k8s context and namespace.
- **0.99.9** — Matrix on Windows/Git Bash (CON / dev/tty).
- **0.99.9.1–0.99.9.5** — Windows matrix: no pipe/dup2 (OSError 22 fix); subprocess capture; stdout/stderr to pipe; smoother refresh; no extra static lines.
- **0.99.9.4–0.99.9.5** — Pipe reader thread (no deadlock on `poco up`); redirect own output so only matrix moves.
- **0.99.9.6–0.99.9.7** — Filter matrix result: Executing before_script, " - ", Docker command lines; with `-V` only merged compose + result.
- **0.99.9.2** — Security: GitPython 3.1.41; README Security; pytest filter; CI pip-audit.
- **0.99.9.8** — Version check timeout (no block without internet); help “Upgrade: pip install --upgrade poco”; new-version message in green blink.
- **0.99.9.9** — `poco status` (Docker Compose projects overview); `-a`/`--all`; subcommand args merged.

### Added in 1.0

- **before_docker_script** — Optional host scripts before Docker: `windows`, `darwin`, `linux` in poco.yml; runs on host before before_script.

## [0.99.9.9] - 2026-02-25

### Added

- **poco status** — Overview of Docker Compose projects currently running (run from any directory). Use `poco status -a` or `poco status --all` to include stopped projects. Global help: `-a --all` with status.

### Changed

- Subcommand options (e.g. `status -a`) are merged into StateHolder.args so commands see their flags. Main help lists `-a --all` for status.

## [0.99.9.8] - 2026-02-25

### Changed

- **Version check** — Does not block startup when there is no internet (5s timeout); on new version shows upgrade command and "pip install --upgrade poco" in the message.
- **Help** — "Upgrade: pip install --upgrade poco" added at the top of the help (`poco -h` / `poco help`).
- **New version notice** — "New version of poco is available" is printed in blinking green in the terminal.

## [0.99.9.7] - 2026-02-25

### Changed

- **Matrix / verbose result** — "Docker command: [...]" lines are now filtered out when showing the final block after the matrix; with `-V` you only see the merged compose and the result ([+] up/down, container table).

## [0.99.9.6] - 2026-02-25

### Changed

- **Matrix result output** — When showing the final block after the matrix, "Executing before_script..." and " - ..." lines are now filtered out so only the real result ([+] up/down, container table) is printed.

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
