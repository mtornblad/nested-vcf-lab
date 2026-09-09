# Build host

Use a maintained amd64 Ubuntu installation for the shared build host. A native
Ubuntu VM is the simplest option. WSL2 is also suitable for the VyOS workflow
when Docker, OVF Tool, and `govc` are installed in or reachable from the Linux
distribution.

Run the preflight check before the first build and after changing the host:

```bash
./orchestration/check-build-host.sh
./orchestration/check-build-host.sh automation
./orchestration/check-build-host.sh all
```

The default target is `vyos`. Select `automation` for the Java/Maven blueprint
toolchain or `all` for both supported umbrella workflows.

## Tool matrix

| Tool | VyOS | VIS | Nested ESXi | Blueprint | Purpose |
| --- | :---: | :---: | :---: | :---: | --- |
| Bash, Git, Make | Required | Required | Required | Required | Source and wrapper commands |
| Python 3.11+ | Required | Tests/docs | OVA packaging | Validation | Validation and packaging scripts |
| Docker Engine | Required | Appliance runtime build | No | No | Privileged VyOS build; VIS installs container services |
| VMware OVF Tool | Required | Required | Recommended | No | OVF/OVA conversion and deployment |
| `govc` | Upload only | Optional | Optional | No | vCenter and Content Library automation |
| Packer | No | Required | Required | No | VIS and ESXi image builds |
| Packer VMware plugin | No | Required | No | No | VIS `vmware-iso` builder |
| Packer vSphere plugin | No | No | Required | No | ESXi `vsphere-iso` builder |
| Java 17 and Maven 3.9+ | No | No | No | Required | Aria Build Tools packaging and publication |
| `jq` | Optional | Optional | Optional | Recommended | Validate rendered VCF deployment JSON |

The current preflight script validates the complete VyOS path and the VCF
Automation Java/Maven path independently. It does not yet validate Packer or
the VIS/ESXi builder plugins.

## Baseline Ubuntu packages

```bash
sudo apt-get update
sudo apt-get install -y \
  ca-certificates \
  curl \
  git \
  gnupg \
  make \
  python3 \
  tar \
  unzip \
  wget \
  zip
```

The component containers and appliance build scripts install their own image
dependencies. Do not install an arbitrary host version of VyOS `live-build`.

## Docker

Install Docker Engine from Docker's maintained Ubuntu repository:

- <https://docs.docker.com/engine/install/ubuntu/>
- <https://docs.docker.com/engine/install/linux-postinstall/>

Verify both the client and daemon:

```bash
docker version
docker info
docker run --rm hello-world
```

The VyOS build container requires `--privileged`. Membership in the `docker`
group effectively grants root-level control of the host and must be treated as
a privileged administrative assignment.

### WSL2

Use one Docker model consistently:

- Docker Desktop with WSL integration enabled for the selected distribution;
  or
- a native Docker Engine running inside that WSL distribution.

Avoid accidentally resolving the Windows Docker client when a native Linux
daemon is expected. Check:

```bash
type -a docker
docker context show
docker info --format 'Docker root: {{.DockerRootDir}}'
```

## Packer

Install Packer using HashiCorp's maintained instructions:

- <https://developer.hashicorp.com/packer/install>

Then install only the plugins required by the component being built:

```bash
packer version

# VIS: vmware-iso builder
packer plugins install github.com/hashicorp/vmware

# Nested ESXi: vsphere-iso builder
packer plugins install github.com/vmware/vsphere

packer plugins installed
```

VIS uses the VMware plugin and nested ESXi uses the vSphere plugin. Follow the
component's pinned template syntax; both currently use legacy JSON templates
rather than HCL. A future refactor should declare and pin plugins in HCL so a
repeatable `packer init` replaces workstation-global plugin installation.

## Build Tools for VMware Aria

The VCF Automation blueprint pins Build Tools 4.25.0 through its Maven parent.
Install Java 17 and Maven 3.9 or newer, then verify the toolchain:

```bash
java -version
mvn -version
./orchestration/check-build-host.sh automation
./orchestration/run_automation.py test
./orchestration/run_automation.py build
```

Use the [Build Tools documentation](https://vmware.github.io/build-tools-for-vmware-aria/latest/)
for Maven repository and authentication setup. Publication also requires a
private Maven profile for the target VCF Automation endpoint; keep it outside
the repository.

## VMware OVF Tool

Download OVF Tool from Broadcom and install it according to its bundle
instructions:

- <https://developer.broadcom.com/tools/open-virtualization-format-ovf-tool/latest>

Do not commit the installer or an expiring authenticated download URL. Verify:

```bash
ovftool --version
```

The builder forces `LC_ALL=C` when invoking OVF Tool to keep generated metadata
stable and avoid locale-dependent behavior.

## govc

Install `govc` only when vCenter inspection or Content Library upload is
required:

- <https://github.com/vmware/govmomi/blob/main/govc/README.md>

Verify connectivity without exposing the password:

```bash
export GOVC_URL="vcenter.example.invalid"
export GOVC_USERNAME="administrator@example.invalid"
read -rsp 'vCenter password: ' GOVC_PASSWORD
export GOVC_PASSWORD
export GOVC_INSECURE=false

govc about
```

Use `GOVC_INSECURE=true` only in a controlled lab while the vCenter CA is not
trusted by the build host.

## Capacity

The current preflight recommends at least 8 GiB visible RAM and 40 GiB free
space on the filesystem containing the repository. Also inspect Docker's
backing store, which may live on another virtual disk:

```bash
df -h .
df -i .
docker info --format 'Docker root: {{.DockerRootDir}}'
docker system df
```

Do not run broad cleanup commands until the build inputs and caches that may be
removed have been reviewed.

## Final verification

```bash
./orchestration/check-build-host.sh
./orchestration/run_vyos.py validate
./orchestration/run_vyos.py test
./orchestration/check-build-host.sh automation
./orchestration/run_automation.py validate
./orchestration/run_automation.py test
```

[Getting started](getting-started.md) · [Build workflows](build-workflows.md) ·
[Troubleshooting](troubleshooting.md)
