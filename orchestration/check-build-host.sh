#!/usr/bin/env bash

set -Eeuo pipefail

readonly LAB_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
readonly BUILD_TARGET="${1:-vyos}"
ERRORS=0
WARNINGS=0

if (( $# > 1 )) || [[ "$BUILD_TARGET" != "vyos" && "$BUILD_TARGET" != "automation" && "$BUILD_TARGET" != "all" ]]; then
    printf 'Usage: %s [vyos|automation|all]\n' "$0" >&2
    exit 2
fi

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

printf '%s\n' "Checking ${BUILD_TARGET} build host for ${LAB_ROOT}"

for REQUIRED_COMMAND in bash git make python3; do
    check_command "$REQUIRED_COMMAND"
done

if [[ "$BUILD_TARGET" == "vyos" || "$BUILD_TARGET" == "all" ]]; then
    for REQUIRED_COMMAND in docker ovftool; do
        check_command "$REQUIRED_COMMAND"
    done
fi

if [[ "$BUILD_TARGET" == "automation" || "$BUILD_TARGET" == "all" ]]; then
    for REQUIRED_COMMAND in java mvn; do
        check_command "$REQUIRED_COMMAND"
    done
fi

if command -v python3 >/dev/null 2>&1; then
    if python3 -c 'import sys; raise SystemExit(sys.version_info < (3, 11))'; then
        ok "$(python3 --version)"
    else
        fail "Python 3.11 or newer is required"
    fi
fi

if [[ "$BUILD_TARGET" == "vyos" || "$BUILD_TARGET" == "all" ]]; then
    case "$(uname -m)" in
        x86_64|amd64) ok "Host architecture: $(uname -m)" ;;
        *) fail "The current pinned VyOS dependencies require an amd64/x86_64 host" ;;
    esac
fi

if [[ "$BUILD_TARGET" == "vyos" || "$BUILD_TARGET" == "all" ]] && command -v docker >/dev/null 2>&1; then
    if docker info >/dev/null 2>&1; then
        ok "Docker daemon is reachable by the current user"
    else
        fail "Docker is installed, but its daemon is unavailable to the current user"
    fi
fi

if [[ "$BUILD_TARGET" == "vyos" || "$BUILD_TARGET" == "all" ]] && command -v ovftool >/dev/null 2>&1; then
    if ovftool --version >/dev/null 2>&1; then
        ok "OVF Tool starts successfully"
    else
        fail "ovftool exists but could not be executed"
    fi
fi

if [[ "$BUILD_TARGET" == "vyos" || "$BUILD_TARGET" == "all" ]]; then
    if command -v govc >/dev/null 2>&1; then
        ok "govc is installed; Content Library upload is available"
    else
        warn "govc is optional for building but required for upload"
    fi
fi

COMPONENT_PATHS=()
if [[ "$BUILD_TARGET" == "vyos" || "$BUILD_TARGET" == "all" ]]; then
    COMPONENT_PATHS+=(components/vyos-build components/vyos-ova-builder)
fi
if [[ "$BUILD_TARGET" == "automation" || "$BUILD_TARGET" == "all" ]]; then
    COMPONENT_PATHS+=(components/vcf-automation)
fi

for COMPONENT_PATH in "${COMPONENT_PATHS[@]}"; do
    if [[ -e "${LAB_ROOT}/${COMPONENT_PATH}/.git" ]]; then
        ok "Submodule initialized: ${COMPONENT_PATH}"
    else
        fail "Submodule missing: ${COMPONENT_PATH}; run git submodule update --init --recursive"
    fi
done

if [[ "$BUILD_TARGET" == "automation" || "$BUILD_TARGET" == "all" ]]; then
    if command -v java >/dev/null 2>&1; then
        JAVA_VERSION_LINE="$(java -version 2>&1 | head -n 1)"
        JAVA_MAJOR="$(sed -nE 's/.*version "([0-9]+).*/\1/p' <<<"$JAVA_VERSION_LINE")"
        if [[ "$JAVA_MAJOR" =~ ^[0-9]+$ ]] && (( JAVA_MAJOR >= 17 )); then
            ok "${JAVA_VERSION_LINE}"
        else
            fail "Java 17 or newer is required"
        fi
    fi

    if command -v mvn >/dev/null 2>&1; then
        MAVEN_VERSION="$(mvn --version 2>/dev/null | awk 'NR == 1 {print $3}')"
        if python3 - "$MAVEN_VERSION" <<'PY'
import re
import sys

match = re.match(r"^(\d+)\.(\d+)", sys.argv[1])
raise SystemExit(not match or tuple(map(int, match.groups())) < (3, 9))
PY
        then
            ok "Apache Maven ${MAVEN_VERSION}"
        else
            fail "Maven 3.9 or newer is required"
        fi
    fi
fi

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

if [[ "$BUILD_TARGET" == "vyos" || "$BUILD_TARGET" == "all" ]]; then
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
fi

printf 'Completed with %d error(s) and %d warning(s).\n' "$ERRORS" "$WARNINGS"
(( ERRORS == 0 ))
