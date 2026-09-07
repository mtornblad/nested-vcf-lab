#!/usr/bin/env bash

set -Eeuo pipefail

readonly LAB_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ERRORS=0
WARNINGS=0

ok() {
    printf 'OK:   %s\n' "$*"
}

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    ERRORS=$((ERRORS + 1))
}

warn() {
    printf 'WARN: %s\n' "$*" >&2
    WARNINGS=$((WARNINGS + 1))
}

check_command() {
    local command_name="$1"
    if command -v "$command_name" >/dev/null 2>&1; then
        ok "${command_name}: $(command -v "$command_name")"
    else
        fail "${command_name} is not installed or not in PATH"
    fi
}

printf '%s\n' "Checking build host for ${LAB_ROOT}"

for REQUIRED_COMMAND in bash git make python3 docker ovftool; do
    check_command "$REQUIRED_COMMAND"
done

if command -v python3 >/dev/null 2>&1; then
    if python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
        ok "$(python3 --version)"
    else
        fail "Python 3.11 or newer is required"
    fi
fi

case "$(uname -m)" in
    x86_64|amd64) ok "Host architecture: $(uname -m)" ;;
    *) fail "The current pinned VyOS dependencies require an amd64/x86_64 host" ;;
esac

if command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        ok "Docker daemon is reachable by the current user"
    else
        fail "Docker is installed, but its daemon is unavailable to the current user"
    fi
fi

if command -v ovftool >/dev/null 2>&1; then
    if ovftool --version >/dev/null 2>&1; then
        ok "OVF Tool starts successfully"
    else
        fail "ovftool exists but could not be executed"
    fi
fi

if command -v govc >/dev/null 2>&1; then
    ok "govc is installed; Content Library upload is available"
else
    warn "govc is optional for building but required for upload"
fi

for COMPONENT_PATH in components/vyos-build components/vyos-ova-builder; do
    if [[ -e "${LAB_ROOT}/${COMPONENT_PATH}/.git" ]]; then
        ok "Submodule initialized: ${COMPONENT_PATH}"
    else
        fail "Submodule missing: ${COMPONENT_PATH}; run git submodule update --init --recursive"
    fi
done

if python3 -m json.tool "${LAB_ROOT}/configuration/lab.example.json" >/dev/null 2>&1; then
    ok "configuration/lab.example.json is valid JSON"
else
    fail "configuration/lab.example.json is invalid JSON"
fi

if [[ -f "${LAB_ROOT}/configuration/lab.local.json" ]]; then
    if python3 -m json.tool "${LAB_ROOT}/configuration/lab.local.json" >/dev/null 2>&1; then
        ok "configuration/lab.local.json is valid JSON"
    else
        fail "configuration/lab.local.json is invalid JSON"
    fi
else
    warn "configuration/lab.local.json has not been created"
fi

AVAILABLE_KIB="$(df -Pk "$LAB_ROOT" | awk 'END {print $4}')"
if (( AVAILABLE_KIB >= 40 * 1024 * 1024 )); then
    ok "At least 40 GiB disk space is available"
else
    warn "Less than the recommended 40 GiB disk space is available"
fi

if [[ -r /proc/meminfo ]]; then
    MEMORY_KIB="$(awk '/^MemTotal:/ {print $2}' /proc/meminfo)"
    if (( MEMORY_KIB >= 8 * 1024 * 1024 )); then
        ok "At least 8 GiB RAM is visible"
    else
        warn "Less than the recommended 8 GiB RAM is visible"
    fi
fi

printf 'Completed with %d error(s) and %d warning(s).\n' "$ERRORS" "$WARNINGS"
(( ERRORS == 0 ))
