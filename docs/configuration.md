# Configuration

The repository has three distinct configuration phases. Keeping them separate
prevents build credentials from becoming appliance defaults and prevents
runtime network values from being baked into reusable OVAs.

| Phase | Examples | Storage |
| --- | --- | --- |
| Build and publish | vCenter URL, Content Library, CPU, memory, OVA name | `configuration/lab.local.json` or environment |
| Appliance contract | OVF property definitions and safe defaults | Component source templates |
| Deployment and first boot | Hostname, IP, gateway, service flags, supplemental configuration | CCI/VM Operator blueprint or deployment input |

## Umbrella configuration

The committed template is `configuration/lab.example.json`. Create a private
overlay at `configuration/lab.local.json`:

```bash
cp configuration/lab.example.json configuration/lab.local.json
chmod 600 configuration/lab.local.json
```

The schema is `nested-vcf-lab.config/v1` and currently requires `general`,
`vyos`, and `esxi` objects.

### General settings

| Field | Purpose | Sensitive |
| --- | --- | :---: |
| `vcenter_url` | vCenter SDK endpoint | No |
| `vcenter_username` | vCenter account | Usually |
| `vcenter_password` | vCenter password | Yes |
| `vcenter_insecure` | Disable certificate verification for lab use | No |
| `content_library` | Upload target | No |
| `artifacts_directory` | Shared artifact root | No |

The adapter maps vCenter settings to `GOVC_URL`, `GOVC_USERNAME`,
`GOVC_PASSWORD`, and `GOVC_INSECURE`. Existing environment values win over the
JSON file, which makes CI secret injection possible without generating a file.

### VyOS settings

| Group | Fields |
| --- | --- |
| Source | `source_directory`, `source_branch`, optional `source_revision` |
| Builder | `builder_directory`, `build_by`, `custom_packages` |
| Appliance | `display_name`, `cpus`, `memory_mb`, `network_adapters`, `network_name` |
| Output | `artifact_subdirectory`, `ova_name` |
| Upload | `template_name` plus inherited general settings |

Run this to inspect the effective component configuration with secrets
redacted:

```bash
./orchestration/run_vyos.py show
```

## Precedence

For umbrella-driven VyOS builds, precedence is:

1. VyOS OVA Builder committed defaults.
2. Optional VyOS component-local configuration.
3. Environment generated from umbrella configuration.
4. Environment variables already set by the invoking process.

The final step is intentional: a CI secret or explicit one-shot override must
not be overwritten by a local file.

## Runtime VyOS properties

The OVA exposes the following property contract. Property IDs in the OVF
template omit the class prefix; VMware Tools exposes them to the guest as
`guestinfo.<key>`.

| Property ID | Guest key | Purpose |
| --- | --- | --- |
| `hostname` | `guestinfo.hostname` | System hostname |
| `password` | `guestinfo.password` | `vyos` account password |
| `ipaddress` | `guestinfo.ipaddress` | Static IPv4 address; empty or `dhcp` enables DHCP |
| `netmask` | `guestinfo.netmask` | Prefix length or dotted netmask |
| `gateway` | `guestinfo.gateway` | Default IPv4 gateway |
| `dns` | `guestinfo.dns` | Comma- or space-separated DNS servers |
| `domain` | `guestinfo.domain` | System domain |
| `ntp` | `guestinfo.ntp` | Comma- or space-separated NTP servers |
| `vlan` | `guestinfo.vlan` | Optional management VLAN ID |
| `enable_ssh` | `guestinfo.enable_ssh` | Enable SSH using VyOS defaults |
| `ssh_authorized_key` | `guestinfo.ssh_authorized_key` | Public key for the `vyos` account |
| `enable_rest` | `guestinfo.enable_rest` | Enable the HTTPS REST API |
| `rest_api_key` | `guestinfo.rest_api_key` | Full-access REST key |
| `management_network` | `guestinfo.management_network` | OVF network used for management-interface discovery |
| `trunk_network` | `guestinfo.trunk_network` | OVF network used for trunk-interface discovery |
| `config_base64` | `guestinfo.config_base64` | Supplemental `set` and `delete` commands |

Password and API-key properties have empty OVA defaults. Deployment tools may
display either the unqualified property ID or the guest-visible key. Query the
actual `ClusterVirtualMachineImage` and use the keys expected by the installed
VM Operator version.

## Supplemental VyOS configuration

Use dedicated properties for stable bootstrap values and `config_base64` for
topology-specific VyOS commands. The payload:

- is UTF-8 text;
- allows blank lines and comments;
- accepts only `set` and `delete` commands;
- is parsed without shell evaluation;
- is applied before dedicated properties;
- may use `__MANAGEMENT_INTERFACE__` and `__TRUNK_INTERFACE__` as standalone
  interface arguments.

Example source file:

```text
set interfaces ethernet __TRUNK_INTERFACE__ mtu 8000
set interfaces ethernet __TRUNK_INTERFACE__ vif 1601 address 172.16.1.1/24
set nat source rule 100 outbound-interface name __MANAGEMENT_INTERFACE__
set nat source rule 100 translation address masquerade
```

Encode it without line wrapping on GNU systems:

```bash
base64 -w0 vyos-extra.conf
```

Base64 is transport encoding, not encryption. Do not place passwords or API
keys in the supplemental payload.

## Component configuration maturity

| Component | Current configuration model | Umbrella integration |
| --- | --- | --- |
| VyOS OVA Builder | Defaults, ignored local JSON, environment | Complete |
| VIS | Multiple Packer JSON var files and OVF properties | Not yet translated by umbrella |
| Nested ESXi | Packer JSON variable file and guestinfo properties | `esxi` section exists, runner not implemented |
| VCF Automation Blueprint | Encrypted request inputs plus structured blueprint variables | Pinned Build Tools submodule; package and publish from the component |

The VIS and nested ESXi component guides identify legacy committed values that
must be removed before their umbrella adapters are considered complete.

[Security](security.md) · [VyOS OVA Builder](components/vyos-ova-builder.md) ·
[Deployment](deployment.md)
