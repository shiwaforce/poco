#!/usr/bin/env bash
set -euo pipefail

REPO_OWNER="shiwaforce"
REPO_NAME="poco"

log(){ echo -e "▶ $*"; }
ok(){ echo -e "✅ $*"; }
warn(){ echo -e "⚠ $*"; }
die(){ echo -e "❌ $*" >&2; exit 1; }

# =====================================================
# Platform detect
# =====================================================
UNAME="$(uname -s)"
PLATFORM="unknown"
case "$UNAME" in
    Linux*) grep -qi microsoft /proc/version 2>/dev/null && PLATFORM="wsl" || PLATFORM="linux" ;;
    Darwin*) PLATFORM="mac" ;;
    MINGW*|MSYS*|CYGWIN*) PLATFORM="windows-gitbash" ;;
    *) die "Nem támogatott platform: $UNAME" ;;
esac
log "Platform: $PLATFORM"

# =====================================================
# Python detect
# =====================================================
PYTHON_BIN=""
if [[ "$PLATFORM" == "windows-gitbash" ]]; then
    PYTHON_BIN="$(command -v py || command -v python || true)"
else
    PYTHON_BIN="$(command -v python3 || command -v python || true)"
fi
[ -n "$PYTHON_BIN" ] || die "Python nem található"
PY_VERSION="$($PYTHON_BIN -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')"
log "Python: $PYTHON_BIN ($PY_VERSION)"
if ! "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 14, 10) else 1)'; then
    PY_FULL="$($PYTHON_BIN -c 'import sys; print("%d.%d.%d" % sys.version_info[:3])')"
    warn "A támogatott Python a 3.14.10 (2026-10-25, sérülékenységi javítások). Jelenlegi: ${PY_FULL}."
fi

# =====================================================
# RESET MODE
# =====================================================
if [[ "${1:-}" == "--reset" ]]; then
    warn "POCO teljes reset..."
    pkill -f poco 2>/dev/null || true
    pkill -f python 2>/dev/null || true
    [[ "$PLATFORM" =~ MINGW|MSYS|CYGWIN ]] && taskkill //F //IM python.exe 2>/dev/null || true
    command -v pipx >/dev/null 2>&1 && pipx uninstall poco 2>/dev/null || true
    for BASE in "$HOME/.local/pipx" "$HOME/AppData/Local/pipx" "$HOME/.local/share/pipx"; do
        [ -d "$BASE/venvs/poco" ] && rm -rf "$BASE/venvs/poco" && warn "Removed $BASE/venvs/poco"
    done
    rm -f "$HOME/.local/bin/poco" "$HOME/.local/bin/poco.exe" 2>/dev/null || true
    hash -r 2>/dev/null || true
    ok "POCO teljesen eltávolítva."
    exit 0
fi

# =====================================================
# pipx install/ensurepath
# =====================================================
PIPX_BIN="$(command -v pipx || true)"
PIPX_AS_MODULE=false

run_pipx() {
    if [[ "$PIPX_AS_MODULE" == true ]]; then
        "$PIPX_BIN" -m pipx "$@"
    else
        "$PIPX_BIN" "$@"
    fi
}

if [[ -z "$PIPX_BIN" ]]; then
    warn "pipx nincs telepítve, telepítés indul..."
    if "$PYTHON_BIN" -c 'import sys; raise SystemExit(0 if sys.prefix == sys.base_prefix else 1)'; then
        "$PYTHON_BIN" -m pip install --user pipx
        PIPX_BIN="$PYTHON_BIN"
        PIPX_AS_MODULE=true
    else
        # pip --user is forbidden inside a virtual environment. Bootstrap pipx
        # in its own user-owned venv so installations work from activated venvs too.
        PIPX_BOOTSTRAP="$HOME/.local/share/poco/pipx-bootstrap"
        "$PYTHON_BIN" -m venv "$PIPX_BOOTSTRAP"
        PIPX_BOOTSTRAP_PYTHON="$PIPX_BOOTSTRAP/bin/python"
        if [[ "$PLATFORM" == "windows-gitbash" ]]; then
            PIPX_BOOTSTRAP_PYTHON="$PIPX_BOOTSTRAP/Scripts/python.exe"
        fi
        "$PIPX_BOOTSTRAP_PYTHON" -m pip install --upgrade pip pipx
        PIPX_BIN="$PIPX_BOOTSTRAP_PYTHON"
        PIPX_AS_MODULE=true
    fi
    run_pipx ensurepath
fi
ok "pipx rendben"

# Make the just-installed pipx applications available to this script as well.
if [[ "$PLATFORM" != "windows-gitbash" ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

# =====================================================
# Régi POCO eltávolítása
# =====================================================
run_pipx uninstall poco 2>/dev/null || true

# =====================================================
# Telepítés pipx-szel (GitHub master elsődleges, hogy a curl one-liner
# valóban a letöltött install.sh-hoz tartozó verziót telepítse)
# =====================================================
TARBALL_URL="https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/master.tar.gz"
log "Telepítés GitHub master tarball-ból..."
if run_pipx install "$TARBALL_URL" --python "$PYTHON_BIN" --force; then
    ok "poco telepítve GitHub master tarball-ból"
else
    warn "GitHub telepítés sikertelen, fallback: PyPI..."
    run_pipx install poco --python "$PYTHON_BIN" --force
    ok "poco telepítve PyPI-ról"
fi

# =====================================================
# Ellenőrzés
# =====================================================
command -v poco >/dev/null 2>&1 || die "poco nincs a PATH-ban. Nyiss új shellt."
ok "poco telepítve: $(command -v poco)"

# =====================================================
# Self-update opció
# =====================================================
SELF_PATH=""
set +u
[[ -n "${BASH_SOURCE[0]:-}" ]] && SELF_PATH="${BASH_SOURCE[0]}"
set -u
UPDATE_URL="https://raw.githubusercontent.com/$REPO_OWNER/$REPO_NAME/master/install.sh"

if [[ "${1:-}" == "--update" ]]; then
    if [[ -z "$SELF_PATH" ]]; then
        SAVED="$HOME/.poco/install.sh"
        mkdir -p "$(dirname "$SAVED")"
        curl -fsSL "$UPDATE_URL" -o "$SAVED"
        chmod +x "$SAVED"
        ok "Script mentve: $SAVED (következő --update: $SAVED --update)"
        exit 0
    fi
    warn "Self-update indul..."
    curl -fsSL "$UPDATE_URL" -o "$SELF_PATH"
    chmod +x "$SELF_PATH"
    ok "Self-update kész, futtasd újra a scriptet."
    exit 0
fi

# Matrix effect is opt-in. Same prompt as `poco matrix` (English, saved to ~/.poco/settings.yml).
if [ -t 0 ] && [ -t 1 ]; then
    poco matrix
else
    echo "Matrix effect is off. Enable with: poco matrix on"
fi

echo ""
echo "Teszt:"
echo "  poco --help"
echo "  poco -V"
ok "Installation complete."