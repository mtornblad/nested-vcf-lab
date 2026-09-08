# Service placement

VyOS, VIS, and the surrounding network may all be capable of providing parts
of the same infrastructure. Select an ownership model before deployment so
clients receive one coherent DNS, DHCP, and time configuration.

## Service capability matrix

| Service | VyOS | VIS | Existing infrastructure |
| --- | --- | --- | --- |
| Routing and static routes | Primary | No | Optional upstream routing |
| Source NAT | Primary | No | Optional upstream NAT |
| DNS forwarding | Supported | Supported through Unbound | Common |
| Authoritative lab records | Supported for simple zones | Supported with forward/reverse record management | Preferred when available |
| DHCP | Supported by VyOS | Supported through dnsmasq | Common |
| NTP server/client | Supported | Supported through Chrony | Common |
| Software depot | No | Yes | Optional external web repository |
| SFTP backup | No | Yes | Optional external SFTP server |
| Container registry | No | Yes, Harbor | Optional enterprise registry |
| LDAP | No | Yes, OpenLDAP | Optional enterprise directory |
| OIDC | No | Yes, Keycloak | Optional enterprise identity provider |
| KMIP KMS | No | Yes, PyKMIP | Preferred external KMS for production |
| Shared service certificates | No control plane | Yes | Enterprise PKI preferred when available |

## Deployment models

### Existing infrastructure

Use this when DNS, DHCP, NTP, identity, backup, and registry services already
exist and are reachable from the nested networks.

- Deploy VyOS only for routing and NAT.
- Point VCF and ESXi directly at existing DNS and NTP.
- Deploy VIS only if its depot, backup, registry, or test identity services add
  value.

### Self-contained lab

Use this when the nested environment must operate independently.

- Deploy VyOS first for routing and egress.
- Provide temporary bootstrap DNS/NTP on VyOS or deploy VIS before VCF
  Installer.
- Use VIS for service lifecycle, health checks, record management, depot,
  backup, registry, and optional identity/KMS functions.
- Migrate clients deliberately if a temporary VyOS service is replaced by VIS.

### Minimal demonstration

For a short-lived demonstration, VyOS can provide routing, NAT, simple DNS, and
time configuration while VIS is omitted. This minimizes VM count but gives up
VIS service management and the additional VCF-specific facilities.

## Recommended ownership record

Record the decision in deployment configuration or an environment runbook:

| Question | Example decision |
| --- | --- |
| Who owns the forward zone? | VIS DNS |
| Who owns reverse zones? | Same VIS instance |
| What resolver do ESXi and VCF use? | VIS address |
| What forwards external queries? | VIS to upstream resolvers |
| What provides DHCP, if any? | External DHCP or exactly one VIS/VyOS scope |
| What provides NTP? | VIS forwarding to external sources |
| What remains on VyOS? | Routing, VLAN gateways, default route, egress NAT |

## VIS management of VyOS

**Target:** VIS may become an optional control plane for selected VyOS desired
state through the VyOS HTTPS API. That integration is not implemented in the
current umbrella revision.

When introduced, it should:

- use a dedicated least-privilege API credential;
- validate current state before changing it;
- show a generated configuration diff;
- commit atomically and report errors without losing the last known-good state;
- avoid owning arbitrary configuration outside its declared scope;
- keep bootstrap possible when VIS itself depends on VyOS routing.

The dependency direction matters: VyOS must be able to establish basic network
reachability before VIS attempts to manage it.

## Production boundary

VIS can be useful in small controlled environments, but the presence of a UI
does not replace availability, backup, monitoring, support, PKI, and security
design. Use established production services whenever those requirements exceed
the appliance's intended lab and proof-of-concept scope.

[VIS component](components/vis.md) · [Network architecture](networking.md) ·
[Roadmap](roadmap.md)
