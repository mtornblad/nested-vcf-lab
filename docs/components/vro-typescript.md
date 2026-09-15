# Orchestrator TypeScript component

The new component contains vRO/VCF Operations Orchestrator workflows and
actions. It has its own Maven project and is intended to be pinned as the
`components/vro-typescript` submodule from `mtornblad/nested-vcf-orchestrator`.
The blueprint and its CCI/custom-resource definitions stay in
`components/vcf-automation`.

## Initial integration status

The component scaffold and umbrella adapter are prepared. The component's
GitHub repository must be created and populated before its gitlink is added
to the umbrella. This draft deliberately does not register an unreachable
submodule. Once the repository is populated:

```bash
git submodule add -b main \
  git@github.com:mtornblad/nested-vcf-orchestrator.git \
  components/vro-typescript
git add .gitmodules components/vro-typescript
```

Commit that registration into the integration branch before merging it.
Subsequent updates follow the normal component-first commit/push process.

## Configuration

Add this section to private umbrella configuration, preserving other sections:

```json
{
  "orchestrator": {
    "builder_directory": "components/vro-typescript",
    "artifact_subdirectory": "vro",
    "maven_profile": "lab"
  }
}
```

The selected profile is `--profile`, then `VRO_PROFILE`, then
`orchestrator.maven_profile`. If the latter is absent, the adapter inherits
`automation.maven_profile`. It works with an existing configuration file that
does not yet contain `orchestrator`. Target credentials remain in private Maven
settings or environment variables referenced there. The profile's `vro.*`
properties are separate from its VCFA properties even when the profile ID is shared.

## Build and publish

Use Build Tools 4.25.0, matching the blueprint, Java 17, Maven 3.9+, Node.js
22.13+ within major 22, and npm 10.9.2+. The Node/npm requirements come from the
[pinned toolchain](https://github.com/vmware/build-tools-for-vmware-aria/blob/v4.25.0/typescript/vrotsc/package.json).
Maven installs the component's Node dependencies.

```bash
./orchestration/check-build-host.sh vro
./orchestration/run_vro.py show
./orchestration/run_vro.py validate
./orchestration/run_vro.py test
./orchestration/run_vro.py build
./orchestration/run_vro.py upload
./orchestration/run_vro.py upload --profile integration
```

`validate` is an offline metadata check. `test` runs the Maven TypeScript/Jasmine
lifecycle. `build` produces a native Orchestrator `.package`; `upload` builds
and imports it using the selected profile. Successful builds/uploads copy the
package from the component's `target/` into `artifacts/vro/builds/`.
`clean` only invokes local Maven cleanup.

## Source direction and runtime boundary

TypeScript builds flow from Git through the transpiler into Orchestrator
JavaScript. Pulling server content back into TypeScript is unsupported, so
`run_vro.py pull` and `download` explain the limitation and stop before invoking
Maven. Retrieve TypeScript changes through Git. See the
[upstream workflow](https://vmware.github.io/build-tools-for-vmware-aria/latest/usage/products/vro/typescript/).

The starter action and workflow only validate and return a lab FQDN. They do
not call the lab or modify resources. Integrations can be added as reviewed
workflows/actions while the blueprint retains their resource declarations.

## Validation boundary

The scaffold's metadata and the umbrella adapter can be checked without an
Orchestrator endpoint. Actual transpilation, `.package` assembly, Jasmine
execution, and workflow import still require the configured build toolchain.
The initial scaffold has not been imported into a live Orchestrator.

[Components](index.md) · [Build host](../build-host.md) ·
[Configuration](../configuration.md) · [Build workflows](../build-workflows.md)
