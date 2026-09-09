# Roadmap

The roadmap separates stabilization from new automation. It is descriptive,
not a release commitment.

## Current foundation

- Umbrella repository with pinned component revisions.
- Shared vCenter, Content Library, artifact, and VyOS build configuration.
- Component-selective build-host preflight for the VyOS and VCF Automation
  workflows.
- Tested VyOS OVA creation, secure vApp property injection, deterministic NIC
  discovery, postconfig initialization, and Content Library upload.
- Mature component-level VIS service catalog and documentation.
- Pinned Aria Build Tools project with an umbrella runner, encrypted request
  inputs, a data-driven ESXi host list, optional per-host NVMe vSAN capacity,
  source contract tests, and offline rendered-spec validation.

## Priority 1: secure and normalize component inputs

- Remove lab-specific values and credentials from tracked VIS and nested ESXi
  configuration.
- Rotate every credential previously committed.
- Introduce generic examples, ignored local overlays, environment overrides,
  validation, and recursive redaction.
- Align artifact paths on the component-first layout.

## Priority 2: complete umbrella adapters

- Add `run_vis.py` with validate, test, build, upload, and show actions.
- Refactor nested ESXi, then add `run_esxi.py` with the same operator contract.
- Extend `check-build-host.sh` with component-selective Packer/plugin checks.
- Emit a common redacted build-manifest shape for every appliance.
- Capture timestamped build logs automatically.

## Priority 3: harden rolling builds

- Preflight the kernel/package relationship before starting expensive
  `live-build` work.
- Record the Docker base image digest and all relevant package-source metadata.
- Define an update policy for the VyOS fork and umbrella gitlink.
- Evaluate immutable package snapshots or a controlled artifact cache when
  longer-term reproducibility is required.

## Priority 4: harden deployment automation

- Replace lab-specific image IDs, region, zone, VM classes, and storage policy
  with a reviewed environment configuration contract.
- Split the full blueprint into reusable modules if Build Tools and the target
  VCF Automation release can preserve dependency and output behavior.
- Add platform-side render tests in addition to the current source contract
  tests, especially for generated JSON and conditional resources.
- Add a safe handoff workflow for the secret-bearing VCF deployment JSON.
- Validate supported VM Operator API and OVF property versions before publish.

## Priority 5: integrate VIS and VyOS

- Define a narrow desired-state contract for DNS, DHCP, NTP, and selected
  routing-related settings.
- Add least-privilege VyOS REST credentials and trust configuration.
- Let VIS display planned changes and effective VyOS state.
- Preserve bootstrap independence: basic VyOS routing must not require VIS.
- Prevent overlapping ownership of authoritative DNS zones or DHCP scopes.

## Priority 6: end-to-end verification

- Build every appliance from a clean Ubuntu host.
- Upload and synchronize Content Library items.
- Deploy through Supervisor and VM Operator.
- Verify OVF transport, NIC mapping, first-boot idempotence, and interactive
  configuration permissions.
- Test routing, NAT, DNS forward/reverse lookup, NTP, MTU, nested ESXi
  customization, and VCF Installer validation.
- Publish a repeatable end-to-end validation report for the sanitized
  blueprint.

## Definition of a supported component

A component is marked supported only when it has:

1. generic committed defaults and ignored secret-bearing overrides;
2. validation and secret redaction;
3. automated unit or contract tests;
4. a reproducible build manifest and controlled artifact paths;
5. an umbrella runner with consistent actions;
6. documented build, upload, deployment, verification, and failure recovery;
7. one successful clean-host end-to-end verification.

[Architecture](architecture.md) · [Component overview](components/index.md) ·
[Development](development.md)
