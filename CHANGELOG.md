# Changelog

All notable changes to poco are documented here.

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
