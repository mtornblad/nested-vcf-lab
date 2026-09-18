# Orchestrator TypeScript component

The new component contains vRO/VCF Operations Orchestrator workflows and
actions. It has its own Maven project and is pinned as the
`components/vro-typescript` submodule from `mtornblad/nested-vcf-orchestrator`.
The blueprint and its CCI/custom-resource definitions stay in
`components/vcf-automation`.

The package also includes 14 imported workflows, 10 actions and their forms
under `native/`. These provide the VCF and certificate implementations referenced
by the blueprints. IDs are preserved and the native source is included in the
same package as TypeScript. See the
[native integration guide](https://github.com/mtornblad/nested-vcf-orchestrator/blob/main/docs/custom-resources.md)
for the external Configurator dependency, source changes and retained limitations.

## Component checkout

The repository and submodule are registered. Initialize both automation components:

```bash
git submodule update --init components/vcf-automation components/vro-typescript
```

Updates follow the normal component-first commit/push process. The new
[modular lab flow](../modular-vro.md) lives under `src/lab` and provides
the request form, catalog configuration workflow, and deployment sequence.

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

The starter action and workflow under `src/lab` only validate and return a lab
FQDN. The new `src/lab` workflows configure catalog IDs and request four
separate blueprints through the VCFA plugin. Their resource declarations stay
in the automation component. See the [modular guide](../modular-vro.md) before
running a deployment.

## Validation boundary

Metadata, the umbrella adapter, pure TypeScript/Jasmine logic, and the official
4.25.0 vRO transpilation have been checked locally. Full Maven `.package`
assembly, import and workflow execution still need verification against the
configured environment.

The imported source additionally passes seven native regression tests and
cross-repository ID/parameter checks. A combined package was built with the
official 4.25.0 packager and inspected for all imported IDs and forms. The
component version is 3.0.2-SNAPSHOT because Build Tools stamps its package
version onto elements and the imported certificate workflows were already 3.0.0.

[Components](index.md) · [Build host](../build-host.md) ·
[Configuration](../configuration.md) · [Build workflows](../build-workflows.md)
