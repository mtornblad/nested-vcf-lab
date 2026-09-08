# Roadmap

The roadmap separates stabilization from new automation. It is descriptive,
not a release commitment.

## Current foundation

- Umbrella repository with pinned component revisions.
- Shared vCenter, Content Library, artifact, and VyOS build configuration.
- Build-host preflight for the complete VyOS workflow.
- Tested VyOS OVA creation, secure vApp property injection, deterministic NIC
  discovery, postconfig initialization, and Content Library upload.
- Mature component-level VIS service catalog and documentation.

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

## Priority 4: version deployment automation

- Add reusable CCI/VM Operator blueprint modules to source control.
- Make ESXi host count data-driven rather than fixed at three hosts.
- Define IP pools, DNS, NTP, passwords, and product credentials once in
  structured inputs.
- Generate VCF host specifications and deployment outputs from the same host
  list.
- Keep runtime secrets in secret-aware deployment inputs rather than blueprint
  defaults.
- Add schema and render tests for supported platform/API versions.

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
- Publish a sanitized reference blueprint and a repeatable validation report.

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
