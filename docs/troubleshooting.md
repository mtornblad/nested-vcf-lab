# Troubleshooting

Start with the first concrete failure, not the final wrapper exception. Preserve
the complete command output and record the component commit before changing the
workspace.

## Collect baseline state

```bash
git rev-parse --short HEAD
git submodule status
git status --short
./orchestration/check-build-host.sh
./orchestration/run_vyos.py show
docker version
ovftool --version
govc version
```

`show` is safe for normal diagnostics because secret fields are redacted.

## Capture a VyOS build log

```bash
mkdir -p artifacts/vyos/logs
BUILD_LOG="artifacts/vyos/logs/vyos-build-$(date -u +%Y%m%dT%H%M%SZ).log"

set -o pipefail
./orchestration/run_vyos.py build 2>&1 | tee "$BUILD_LOG"
BUILD_RC=${PIPESTATUS[0]}
printf 'Build exit code: %s\nLog: %s\n' "$BUILD_RC" "$BUILD_LOG"
```

Find likely root errors with context:

```bash
grep -nEi -C 10 \
  '(^E:|^Err:|No space left|Failed to fetch|Unable to locate|NO_PUBKEY|dpkg: error|permission denied)' \
  "$BUILD_LOG" | head -n 250
```

## Docker daemon unavailable

Symptoms include `Cannot connect to the Docker daemon` or a Windows Docker
binary being selected unexpectedly in WSL2.

```bash
type -a docker
docker context show
docker info
```

Enable Docker Desktop integration for the selected WSL distribution or start
the native Linux daemon, depending on the chosen model. Do not mix both models
in one shell configuration.

## Permission denied on generated Python files

An interrupted privileged build may leave root-owned files in
`artifacts/vyos/work/vyos-build`. The current builder records ownership state,
repairs foreign-owned entries with container root, and restores the complete
disposable checkout to the invoking UID/GID.

Inspect before intervening:

```bash
find artifacts/vyos/work/vyos-build -xdev \
  \( ! -uid "$(id -u)" -o ! -gid "$(id -g)" \) -ls | head -n 100
```

Retry the current build first. Do not use recursive `sudo` against the
repository or reset the source submodule.

## `lb build` failed

The final exception:

```text
OSError: Command 'lb build 2>&1' failed
```

is only a summary. Search earlier in the captured log for the first APT,
package, mount, or filesystem error.

### Missing `linux-image-<version>-vyos`

This normally means the pinned rolling source requests a kernel version no
longer available in the rolling package repository. Update the `vyos-build`
fork and umbrella gitlink using [VyOS Build](components/vyos-build.md), then
pull the current builder image:

```bash
docker pull vyos/vyos-build:current
./orchestration/run_vyos.py build
```

Do not patch the kernel version by hand.

## Disk checks

Repository space and Docker storage may use different filesystems:

```bash
df -h .
df -i .
docker info --format 'Docker root: {{.DockerRootDir}}'
docker system df
```

Review cache contents before pruning. A large reclaimable value is not itself
an error when sufficient space remains.

## OVF Tool not found or fails to start

```bash
type -a ovftool
ovftool --version
```

Install the Linux bundle on the build host and ensure the executable is in the
same environment that runs the orchestration command. Avoid relying on a
Windows path from WSL unless that exact integration has been tested.

## Content Library upload failures

### `POST /sdk: 404 Not Found`

`GOVC_URL` points to an HTTPS service that is not vCenter, often an automation
VIP or reverse proxy.

```bash
govc about
./orchestration/run_vyos.py show
```

Correct `general.vcenter_url` in the private configuration or override
`GOVC_URL` explicitly.

### Certificate signed by unknown authority

Preferred fix: install the vCenter CA chain in the build host trust store.
Temporary lab workaround: set `general.vcenter_insecure` to `true` or export
`GOVC_INSECURE=true`. Do not normalize this for production.

### Missing Content Library value

```bash
./orchestration/run_vyos.py validate-upload
govc library.ls
```

Set `general.content_library` to the exact library name.

## Supervisor VM not found by inventory path

Supervisor-managed VMs may be returned by `govc find` using a path that
`object.collect` cannot resolve as a normal inventory path. Use its managed
object ID:

```bash
VM_OBJECT=$(govc find -i / -type m -name '<vm-name>')
govc object.collect -s "$VM_OBJECT" guest.toolsRunningStatus
```

The value should resemble `VirtualMachine:vm-1234`.

## `guestinfo.ovfEnv` returns no value

Check both prerequisites:

```bash
govc object.collect -s "$VM_OBJECT" guest.toolsRunningStatus
govc object.collect -s "$VM_OBJECT" \
  config.vAppConfig.ovfEnvironmentTransport
```

Expected:

```text
guestToolsRunning
com.vmware.guestInfo
```

Inside VyOS:

```bash
sudo systemctl status open-vm-tools.service --no-pager -l
vmtoolsd --cmd 'info-get guestinfo.ovfEnv'
```

If Tools runs but transport is empty, rebuild or republish the OVA with the
current builder and deploy a new VM from the new library item.

## VyOS first boot did not apply

The current image intentionally has no `vapp-init.service`. It starts from the
VyOS postconfig hook.

```bash
sudo test -x /config/scripts/vyos-postconfig-bootup.script
sudo test -x /usr/local/sbin/vyos-vapp-init
sudo grep -F 'vyos-vapp-init' /var/log/messages | tail -n 100
sudo test -e /opt/vyos-ova-builder/vapp-configured \
  && echo 'configured' || echo 'not configured'
```

For a controlled manual retry:

```bash
sudo /usr/local/sbin/vyos-vapp-init
```

The worker re-executes itself with `vyattacfg` as the primary group. A failed
run leaves the marker absent and will be retried on the next boot.

## Interfaces are reversed

Set both `management_network` and `trunk_network` to the actual OVF/VM Operator
network names and use interface tokens in supplemental configuration. Confirm
the log contains two distinct mappings. Never repair this by globally swapping
literal `eth0` and `eth1` in a reusable blueprint.

## Interactive VyOS commit permission error

A historical bootstrap commit could leave
`/opt/vyatta/etc/config/archive/commits` with the wrong group. The current
worker normalizes the archive directory and commit log to the `vyattacfg`
contract before and after its commit. New images should not reproduce the
problem.

On an affected test VM, inspect:

```bash
sudo ls -ld /opt/vyatta/etc/config/archive
sudo ls -l /opt/vyatta/etc/config/archive/commits
```

Prefer rebuilding and redeploying the corrected image over accumulating manual
repairs in the release process.

[Getting started](getting-started.md) · [Build workflows](build-workflows.md) ·
[Deployment](deployment.md)
