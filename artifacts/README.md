# Artifacts

This directory contains downloaded dependencies and generated build artifacts.

## Directories

- `downloads/` – externally downloaded ISO images, packages and dependencies.
- `builds/` – generated ISO, OVA, OVF, VMDK and other build output.
- `manifests/` – tracked dependency manifests, versions, source URLs and checksums.
- `logs/` – build and validation logs.
- `tmp/` – temporary build working directories.

Binary artifacts are intentionally excluded from Git.

Every downloaded dependency should eventually be represented by a tracked
manifest containing at least:

- source URL
- filename
- product version
- SHA-256 checksum
- date retrieved
- license or redistribution note where relevant
