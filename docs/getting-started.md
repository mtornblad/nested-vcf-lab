# Getting started

This guide takes a clean Ubuntu build host from clone to a validated VyOS OVA.
It deliberately separates host installation, private configuration, build, and
publication so failures are easier to diagnose.

## 1. Clone the source set

```bash
git clone --recurse-submodules git@github.com:mtornblad/nested-vcf-lab.git
cd nested-vcf-lab
git submodule status
```

For an existing clone:

```bash
git pull --ff-only
git submodule sync --recursive
git submodule update --init --recursive
```

Every submodule line should begin with a space. A leading `-` means the
submodule has not been initialized, `+` means it is at a different commit, and
`U` indicates a merge conflict.

## 2. Prepare the build host

Install the tools described in [Build host](build-host.md), then run:

```bash
./orchestration/check-build-host.sh
./orchestration/check-build-host.sh automation
```

The complete VyOS path requires Git, Python 3.11 or newer, Docker, OVF Tool,
and an amd64 host. `govc` is required only for Content Library upload. VIS and
nested ESXi additionally require Packer and the appropriate VMware builder
plugin.

## 3. Create private configuration

```bash
cp configuration/lab.example.json configuration/lab.local.json
chmod 600 configuration/lab.local.json
${EDITOR:-vi} configuration/lab.local.json
```

Set at least:

- `general.vcenter_url`
- `general.vcenter_username`
- `general.vcenter_password`
- `general.content_library` before upload
- `vyos.build_by`
- `vyos.template_name`
- `automation.maven_profile` to the profile already defined in Maven

The vCenter URL must identify vCenter itself, not a VCF Automation endpoint or
another HTTPS virtual IP. Validate it independently with:

```bash
govc about
```

See [Configuration](configuration.md) for precedence, field ownership, and
secret handling.

## 4. Validate before building

```bash
./orchestration/run_vyos.py show
./orchestration/run_vyos.py validate
./orchestration/run_vyos.py test
```

`show` redacts secret values. Do not replace it with commands that dump the
private JSON into shared logs.

## 5. Build the VyOS OVA

Capture the complete build output because upstream `live-build` errors often
appear well before the final Python exception:

```bash
mkdir -p artifacts/vyos/logs
BUILD_LOG="artifacts/vyos/logs/vyos-build-$(date -u +%Y%m%dT%H%M%SZ).log"

set -o pipefail
./orchestration/run_vyos.py build 2>&1 | tee "$BUILD_LOG"
BUILD_RC=${PIPESTATUS[0]}

printf 'Build exit code: %s\nLog: %s\n' "$BUILD_RC" "$BUILD_LOG"
```

A successful build produces:

```text
artifacts/vyos/builds/vyos-vmware-vapp.ova
artifacts/vyos/builds/vyos-vmware-vapp.build.json
```

The JSON manifest records the source commit, reproducible configuration,
artifact size, and SHA-256 checksum without upload credentials.

## 6. Upload to Content Library

```bash
./orchestration/run_vyos.py validate-upload
./orchestration/run_vyos.py upload
```

Confirm the imported library item:

```bash
govc library.ls
govc library.info "${CONTENT_LIBRARY_NAME}"
```

Replace the shell variable with the configured library name or export it before
running the second command.

## 7. Deploy and verify

Follow [Deployment and first boot](deployment.md). The essential verification
points are:

1. The Content Library item exposes the expected OVF properties.
2. `config.vAppConfig.ovfEnvironmentTransport` is `com.vmware.guestInfo`.
3. VMware Tools is running inside the guest.
4. `guestinfo.ovfEnv` contains the supplied properties.
5. The VyOS first-boot completion marker exists.

## 8. Build and publish the VCF Automation blueprint

The same private umbrella configuration selects the component and default
Maven profile:

```bash
./orchestration/run_automation.py show
./orchestration/run_automation.py pull
./orchestration/run_automation.py validate
./orchestration/run_automation.py test
./orchestration/run_automation.py build
./orchestration/run_automation.py upload
```

Override only the publication target when needed:

```bash
VCFA_PROFILE=integration ./orchestration/run_automation.py upload
./orchestration/run_automation.py upload --profile integration
```

After a test deployment, copy the raw `vcf_deployment_json` output into a
protected file and validate it:

```bash
umask 077
${EDITOR:-vi} /tmp/vcf-deployment.json
./orchestration/run_automation.py validate-spec \
  --spec /tmp/vcf-deployment.json \
  --allow-secret-references
```

The flag permits a structural check of encrypted Automation references. It is
not valid for the final handoff: materialize credentials in the protected
local copy and rerun without `--allow-secret-references` before importing the
file into VCF Installer.

## Other components

VIS and nested ESXi do not yet have umbrella runner commands. Use their
component guides and treat their current configuration files according to the
limitations documented there:

- [VIS](components/vis.md)
- [Nested ESXi](components/nested-esxi.md)

See [VCF Automation Blueprint](components/vcf-automation.md) before publishing
or deploying it.

[Documentation home](index.md) · [Troubleshooting](troubleshooting.md)
