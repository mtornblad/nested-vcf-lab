# Build host

The umbrella repository uses one host to run the component builders. Run the
preflight check before the first build and after changing the host:

```bash
./orchestration/check-build-host.sh
```

## Required tools

| Tool | Required for | Check |
| --- | --- | --- |
| Bash, Git and Make | Orchestration and source management | `git --version` |
| Python 3.11+ | Configuration and OVA assembly | `python3 --version` |
| Docker Engine | Privileged VyOS image build | `docker info` |
| VMware OVF Tool | VMX-to-OVF conversion | `ovftool --version` |
| govc | Optional Content Library upload | `govc version` |

For Ubuntu, baseline packages can be installed with:

```bash
sudo apt update
sudo apt install -y ca-certificates curl git make python3 unzip zip
```

Install Docker Engine from Docker's maintained Ubuntu repository rather than
the distribution's older compatibility package:

- https://docs.docker.com/engine/install/ubuntu/
- https://docs.docker.com/engine/install/linux-postinstall/

Membership in the `docker` group grants root-equivalent access. On WSL2,
Docker Desktop integration is also suitable if `docker info` works inside the
distribution and privileged Linux containers are enabled.

Download VMware OVF Tool from Broadcom and place `ovftool` in `PATH`:

- https://developer.broadcom.com/tools/open-virtualization-format-ovf-tool/latest

The builder itself does not require `govc`. Install it only when Content
Library upload is needed, following the upstream instructions:

- https://github.com/vmware/govmomi/blob/main/govc/README.md

## Capacity

The preflight script recommends at least 8 GiB RAM and 40 GiB free disk space.
Generated and downloaded data is placed under `artifacts/`, split by component.

## Configuration

Create the private umbrella configuration and restrict its permissions:

```bash
cp configuration/lab.example.json configuration/lab.local.json
chmod 600 configuration/lab.local.json
${EDITOR:-vi} configuration/lab.local.json
```

The private file is ignored by Git. Environment variables still have highest
precedence, which is useful for CI secret injection.

Validate and build VyOS through the umbrella:

```bash
./orchestration/run_vyos.py validate
./orchestration/run_vyos.py test
./orchestration/run_vyos.py build
./orchestration/run_vyos.py validate-upload
./orchestration/run_vyos.py upload
```
