# Modular lab deployment through vRO

The experimental **modular** variant separates lab provisioning into four
blueprints and orders them through a TypeScript workflow in VCF Operations
Orchestrator. The existing Full Stack VCF entry point remains the default.

| Component | New content |
| --- | --- |
| `components/vcf-automation/modular` | Separate Build Tools package: Foundation, ESXi, Installer and Jumphost |
| `components/vro-typescript/src/modular` | Request form, catalog configuration workflow, deployment sequence and VCF JSON generation |
| Umbrella | `--variant modular` selection for blueprint build, upload and download |

Use these component guides for the complete contracts and operating details:

- [Blueprint ownership and input/output contract](https://github.com/mtornblad/nested-vcf-automation/blob/main/modular/README.md)
- [vRO form, configuration, execution and recovery](https://github.com/mtornblad/nested-vcf-orchestrator/blob/main/docs/modular-lab.md)

## Prepare and publish

Initialize the pinned components from the umbrella root:

```bash
git submodule update --init components/vcf-automation components/vro-typescript
./orchestration/check-build-host.sh automation
./orchestration/check-build-host.sh vro
```

Use Java 17, Maven 3.9+, Python 3.11+, Node 22.13+ within major 22, and
npm 10.9.2+ for Build Tools 4.25.0. Install Python validation dependencies in
your active virtual environment:

```bash
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -r components/vcf-automation/modular/requirements.txt
```

Merge these sections into `configuration/lab.local.json`, preserving all
existing settings. The profile IDs reference private Maven settings:

```json
{
  "automation": {
    "builder_directory": "components/vcf-automation",
    "variant": "full-stack",
    "maven_profile": "lab"
  },
  "orchestrator": {
    "builder_directory": "components/vro-typescript",
    "artifact_subdirectory": "vro",
    "maven_profile": "lab"
  }
}
```

Select the trial explicitly for each automation command:

```bash
./orchestration/run_automation.py show --variant modular
./orchestration/run_automation.py test --variant modular
./orchestration/run_vro.py validate
./orchestration/run_vro.py upload
./orchestration/run_automation.py upload --variant modular
```

Both upload commands build their package before publishing it. To build for
review without uploading, use `build` in place of `upload`. The vRO package is
also copied to `artifacts/vro/builds/`; the modular automation package is in
`components/vcf-automation/modular/target/`.

To make this variant the local default, set `automation.variant` to `modular`.
`--variant full-stack` or `--variant modular` overrides the setting for one
command. Profile precedence is unchanged: automation uses `--profile`, then
`VCFA_PROFILE`, then `automation.maven_profile`; vRO uses `--profile`,
`VRO_PROFILE`, `orchestrator.maven_profile`, then `automation.maven_profile`.

## Register the runtime catalog

In VCF Automation, release and expose these four blueprints to the intended
All Apps project:

1. **Nested VCF Modular - Foundation**
2. **Nested VCF Modular - ESXi**
3. **Nested VCF Modular - Installer**
4. **Nested VCF Modular - Jumphost**

Record the four catalog item IDs and the project UUID. In vRO, configure an
authenticated VCFA plugin connection for that organization with shared-session
access to those catalog items. Then run **Nested VCF Lab / Modular /
Configure Modular Catalog** with the IDs and connection SID. Use `lab` as the
runtime profile name if following the default request form.

This runtime profile is a vRO configuration element. It is separate from the
Maven profile with the same name: Maven selects where to upload code; the
runtime profile selects where the workflow orders deployments.

## First request

Run **Deploy Modular VCF Lab**. Its seven-page form groups lab identity,
placement, network/VyOS, ESXi, Installer, Jumphost and recovery inputs. Review
the existing lab's image IDs and VM classes. Use a new lab name and enter a
lab password and VyOS API key; neither has a committed default.

Leave all four stages selected and **Run VCF bring-up** off for the first test.
Foundation owns the namespace, VPC, NAT, networks, DNS/NTP and VyOS. Each child
deployment uses the returned namespace name and creates only its own guest
resources. ESXi count, capacity disks, DNS records and VCF JSON all follow the
same host plan. The Installer receives its own FQDN; SDDC Manager retains a
separate identity.

The new plan retains the checked-in blueprint's vApp keys and MTU defaults.
The present default nested MTU is 8800, with a DVS value 100 bytes higher,
capped at 9000. A form override does not change the underlying VCF/NSX fabric.

The workflow waits for each VCFA deployment using persisted vRO timers and
then starts the next stage. Its outputs include deployment IDs, the public
lab plan, namespace/external IP, and `vcfDeploymentJson` with the supplied
plaintext credentials. Check guest bootstrap, DNS/PTR, Windows routes, NTP
and MTU before proceeding to VCF validation. `VirtualMachineCreated` does not
prove that guest services are ready.

Save the raw JSON output to an ignored file and validate it:

```bash
./orchestration/run_automation.py validate-spec \
  --spec artifacts/vcf-deployment.json
```

Then import it into Installer and run its platform validation. Optional
automatic bring-up uses the VCF and installer-certificate custom resources.
Their workflow implementations are now included in the vRO package as
[editable native source](https://github.com/mtornblad/nested-vcf-orchestrator/blob/main/docs/custom-resources.md).
Upload vRO first, then the Automation definitions. The built-in Configurator
certificate-delete workflow remains an external dependency. Read/Delete VCF
are still placeholders from the export; see the component guide for retained
polling and API-response limitations.

The automation create descriptor now forwards the `sddcSpec` input. Check the
interfaces between the two pinned components before publishing:

```bash
python3 components/vro-typescript/scripts/validate_native.py \
  --automation components/vcf-automation
```

## Recovery, cleanup and source updates

On failure, the workflow retains resources and returns accepted deployment
IDs. Inspect VCFA, then use the Recovery page with those IDs and the same lab
inputs to resume. It validates the project, catalog item and public plan
before placing any additional orders. It does not automatically retry an
ambiguous POST, delete a failed deployment or resize an existing lab.

Delete child deployments before Foundation. Give Foundation a lease at least
as long as the children; existing-namespace references do not create a
cross-deployment deletion dependency.

To retrieve blueprint edits from Automation after committing local changes:

```bash
./orchestration/run_automation.py pull --variant modular
./orchestration/run_automation.py test --variant modular
```

TypeScript source is retrieved through Git; vRO JavaScript cannot be pulled
back into equivalent TypeScript. Commit changes in the relevant component
first, then advance its umbrella gitlink.

## Validation scope

Offline validation covers the modular blueprint schemas/contracts, host and
network plan, VCF JSON generation, catalog sequencing, resume checks, failure
handling and umbrella variant selection. The official 4.25.0 vRO compiler was
also used to generate actions, workflow XML and attached forms.

Full Maven package assembly, import and execution on the target vRO/VCFA
remain to be verified on the configured build host. Provisioning status also
does not replace guest or Installer validation.

[Build workflows](build-workflows.md) · [Configuration](configuration.md) ·
[Orchestrator component](components/vro-typescript.md)
