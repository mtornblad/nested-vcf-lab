# Documentation

This documentation describes the umbrella repository at two levels: the
shared lifecycle across all appliance builders, and the implementation details
of each pinned component.

## Choose a path

| Goal | Start here | Continue with |
| --- | --- | --- |
| Understand the project | [Architecture](architecture.md) | [Repository layout](repository-layout.md) |
| Prepare a new builder | [Getting started](getting-started.md) | [Build host](build-host.md) |
| Configure a lab safely | [Configuration](configuration.md) | [Security](security.md) |
| Build or upload an appliance | [Build workflows](build-workflows.md) | [Troubleshooting](troubleshooting.md) |
| Design the nested network | [Network architecture](networking.md) | [Service placement](service-placement.md) |
| Deploy through vSphere Supervisor | [Deployment](deployment.md) | [VCF Automation Blueprint](components/vcf-automation.md) |
| Obtain a nested ESXi image | [Nested ESXi Packer](components/nested-esxi.md) | [Credits and further reading](references.md) |
| Change the repositories | [Development](development.md) | [Roadmap](roadmap.md) |

## Core concepts

- The umbrella repository owns shared configuration, orchestration adapters,
  artifact policy, and cross-component documentation.
- Each submodule owns its implementation, tests, and component-specific build
  contract.
- A submodule commit is immutable from the umbrella's point of view. Branch
  names in `.gitmodules` assist updates but do not replace the recorded commit.
- Builder inputs, runtime bootstrap properties, and generated deployment
  specifications are separate configuration layers.
- Binary payloads are never source-controlled. Their versions, checksums, and
  source revisions should be recorded instead.

## Documentation map

### Design

- [Architecture](architecture.md)
- [Repository layout](repository-layout.md)
- [Network architecture](networking.md)
- [Service placement](service-placement.md)
- [Security model](security.md)

### Operations

- [Getting started](getting-started.md)
- [Build host](build-host.md)
- [Configuration](configuration.md)
- [Build and publish workflows](build-workflows.md)
- [Deployment and first boot](deployment.md)
- [Troubleshooting](troubleshooting.md)

### Components

- [Component overview](components/index.md)
- [VyOS OVA Builder](components/vyos-ova-builder.md)
- [VyOS Build](components/vyos-build.md)
- [VCF Infrastructure Services Appliance](components/vis.md)
- [Nested ESXi Packer](components/nested-esxi.md)
- [VCF Automation Blueprint](components/vcf-automation.md)

### Project maintenance

- [Development and contribution](development.md)
- [Roadmap](roadmap.md)
- [Credits and further reading](references.md)

## Accuracy convention

Statements labeled **Current** describe behavior present in the pinned source
revision. Statements labeled **Target** describe an intended design that is not
yet fully implemented. This distinction is important because the umbrella
currently orchestrates VyOS but not the complete VIS or nested ESXi lifecycle.

[Back to project README](../README.md)
