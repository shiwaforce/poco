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
if ! command -v pipx >/dev/null 2>&1; then
    warn "pipx nincs telepítve, telepítés indul..."
    "$PYTHON_BIN" -m pip install --user pipx
    "$PYTHON_BIN" -m pipx ensurepath
    echo "⚠ Nyiss új terminált, majd futtasd újra a scriptet."
    exit 0
fi
ok "pipx rendben"

# =====================================================
# Régi POCO eltávolítása
# =====================================================
pipx uninstall poco 2>/dev/null || true

# =====================================================
# Telepítés pipx-szel (PyPI elsődleges – nincs GitHub API rate limit)
# =====================================================
log "Telepítés PyPI-ról..."
if pipx install poco --python "$PYTHON_BIN" --force; then
    ok "poco telepítve PyPI-ról"
else
    warn "PyPI telepítés sikertelen, fallback: GitHub master tarball..."
    TARBALL_URL="https://github.com/$REPO_OWNER/$REPO_NAME/archive/refs/heads/master.tar.gz"
    log "Fallback URL: $TARBALL_URL"
    pipx install "$TARBALL_URL" --python "$PYTHON_BIN" --force
    ok "poco telepítve GitHub tarball-ból (master)"
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

echo ""
echo "Teszt:"
echo "  poco --help"
echo "  poco -V"
ok "Installation complete."