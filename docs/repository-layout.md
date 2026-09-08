# Repository layout

The umbrella repository is intentionally small. Component implementation lives
in submodules, while shared configuration and orchestration remain at the top
level.

```text
nested-vcf-lab/
├── README.md
├── .gitmodules
├── artifacts/
│   ├── README.md
│   └── <component>/
│       ├── downloads/
│       ├── sources/
│       ├── work/
│       ├── builds/
│       └── logs/
├── components/
│   ├── nested-esxi-packer/
│   ├── vis/
│   ├── vyos-build/
│   └── vyos-ova-builder/
├── configuration/
│   ├── .gitignore
│   └── lab.example.json
├── docs/
└── orchestration/
    ├── check-build-host.sh
    ├── lab_config.py
    └── run_vyos.py
```

## Directory ownership

| Path | Owner | Content policy |
| --- | --- | --- |
| `components/<name>/` | Component repository | Commit changes in the component first, then update the parent gitlink |
| `configuration/lab.example.json` | Umbrella repository | Generic, non-secret example values only |
| `configuration/lab.local.json` | Local operator | Private values; ignored by Git and preferably mode `0600` |
| `orchestration/` | Umbrella repository | Thin adapters and cross-component checks, not component implementation |
| `artifacts/` | Build process | Generated or downloaded content; binary payloads are ignored |
| `docs/` | Umbrella repository | Cross-component architecture and operational documentation |

## Submodules

`.gitmodules` records a preferred branch for each component, but Git checks out
the exact commit stored by the umbrella repository. This provides a controlled
bill of source while still allowing deliberate updates.

Initialize an existing clone:

```bash
git submodule sync --recursive
git submodule update --init --recursive
git submodule status
```

Clone everything in one operation:

```bash
git clone --recurse-submodules git@github.com:mtornblad/nested-vcf-lab.git
```

Do not use `git submodule update --remote` as an undocumented routine step. It
changes component inputs and may move a rolling dependency without review.
Follow the controlled process in [Development](development.md).

## Artifact layout

The canonical layout is component-first:

```text
artifacts/<component>/downloads
artifacts/<component>/sources
artifacts/<component>/work
artifacts/<component>/builds
artifacts/<component>/logs
```

The VyOS adapter currently uses `artifacts/vyos/`. Existing build-first
placeholder directories under `artifacts/builds/` and `artifacts/downloads/`
are legacy scaffolding and are not used by `run_vyos.py`; they should be
consolidated when the VIS and ESXi adapters are introduced.

Generated files must not be staged simply because they reside below the
repository root. Before committing, always inspect:

```bash
git status --short
git diff --check
git diff --cached --submodule=log
```

## Component boundaries

- Do not place VyOS guest initialization logic in `orchestration/`; it belongs
  in `vyos-ova-builder`.
- Do not patch the `vyos-build` submodule during an OVA build. Customization is
  copied into a disposable checkout.
- Do not duplicate VIS service documentation in implementation detail. The
  umbrella component page summarizes it and links to the VIS source documents.
- Do not place deployment-specific passwords, private DNS names, image IDs, or
  namespace IDs in committed umbrella configuration.

[Documentation home](index.md) · [Development](development.md) ·
[Artifacts](../artifacts/README.md)
