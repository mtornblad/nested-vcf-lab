# Artifacts

This directory is the shared, non-source workspace for downloaded dependencies,
disposable build state, generated appliances, manifests, and logs.

## Canonical layout

New component adapters should use a component-first structure:

```text
artifacts/
└── <component>/
    ├── downloads/
    ├── sources/
    ├── work/
    ├── builds/
    └── logs/
```

| Directory | Content | Git policy |
| --- | --- | --- |
| `downloads/` | External packages, installers, and other retrieved inputs | Ignore binaries; record versions and checksums |
| `sources/` | Builder-owned mirrors or source caches | Ignore |
| `work/` | Disposable checkouts, container contexts, and packaging state | Ignore |
| `builds/` | ISO, OVA, OVF, VMDK, and associated build records | Ignore binary outputs |
| `logs/` | Timestamped validation and build output | Ignore; review before sharing |

The current VyOS adapter uses `artifacts/vyos/`. Older build-first placeholder
directories remain as legacy scaffolding until VIS and nested ESXi receive
umbrella adapters.

## Dependency records

Every externally downloaded dependency should be represented by committed
metadata in the component BOM or a tracked manifest. At minimum record:

- stable source URL;
- filename and product version;
- architecture where relevant;
- SHA-256 checksum;
- retrieval or publication date when useful;
- license or redistribution restrictions.

Authenticated, expiring download URLs do not belong in Git. Proprietary binary
payloads remain local even when their checksum and expected filename are
documented.

## Build records

Supported builders should create a redacted record next to the final artifact
containing the source commit, non-secret effective configuration, artifact size,
and SHA-256 checksum. Upload credentials and runtime bootstrap secrets must not
appear in that record.

## Safety

- Treat logs and instantiated appliance exports as potentially secret-bearing.
- Never add a broad Git ignore exception for this directory.
- Remove only explicit component work directories after confirming they are
  disposable.
- Do not recursively change ownership outside `artifacts/<component>/work/`.
- Prefer rebuilding an artifact from its manifest over treating a local binary
  as the source of truth.

[Repository layout](../docs/repository-layout.md) ·
[Build workflows](../docs/build-workflows.md) ·
[Security](../docs/security.md)
