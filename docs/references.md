# Credits and further reading

This project combines original integration work with patterns documented by
the VMware community. The links below are references and design lineage; their
content is not copied into this repository and their authors do not endorse or
support this project.

## Acknowledgements

| Source | Why it matters here |
| --- | --- |
| [Tomas Fojta — Building Nested Labs in VCF Automation 9.1](https://fojta.wordpress.com/2026/05/12/building-nested-labs-in-vcf-automation-9-1/) | Practical reference topology for an isolated namespace lab using a dedicated VPC, disconnected subnets, VyOS, guest VLAN bindings, VM groups, and blueprint capture |
| [Tom Fojta's Blog](https://fojta.wordpress.com/) | Continuing field notes on VCF Automation, NSX networking, VKS, and nested lab operation |
| [William Lam — Home Lab](https://williamlam.com/home-lab) | Broad home-lab index covering deployment automation, hardware, and nested virtualization |
| [William Lam — Nested Virtualization](https://williamlam.com/nested-virtualization) | Maintained index for nested ESXi appliances, networking requirements, version-specific guidance, and VCF lab automation |

Special thanks to Tomas Fojta and William Lam for making implementation detail
available to the community. Their work is particularly useful for separating
platform requirements from assumptions that happen to work in one lab.

## Operational guidance repeated locally

These points are repeated because they are part of this repository's deployment
contract and are easy to miss when following a long external article:

1. Place each disposable lab in its own namespace and dedicated VPC when
   isolation between simultaneous deployments is required.
2. Keep the trunk and guest VLAN subnets disconnected from the VPC gateway.
   Bind each VLAN subnet to the trunk with a `SubnetConnectionBindingMap`; VyOS
   owns routing between those networks and the uplink.
3. Publish a VM Class that exposes hardware-assisted virtualization before
   starting nested ESXi. Make the class available through the appropriate
   region quota and namespace policy.
4. Use an ESXi appliance version compatible with the intended VCF release and
   bill of materials. A newer image is not automatically a compatible image.
5. Confirm that the project Content Library image is available to VM Operator
   and that its OVF properties match the blueprint before deployment.
6. Treat blueprint capture as a starting point. Validate resources that may not
   be captured completely, including subnet bindings, network customization,
   boot ordering, and deployment outputs.

The local implementation deliberately differs from a manual ISO workflow:
VyOS is built as an OVA with `open-vm-tools`, VMware Tools OVF transport, vApp
properties, deterministic NIC-role discovery, and an idempotent first-boot
hook. See [VyOS OVA Builder](components/vyos-ova-builder.md).

## Source and license responsibility

External posts are implementation guidance, not vendor support statements.
Broadcom product documentation, the target VCF bill of materials, license
terms, and support policy remain authoritative. Do not redistribute ESXi ISOs,
OVAs, or other vendor binaries through this repository.

[Documentation home](index.md) · [Nested ESXi Packer](components/nested-esxi.md) ·
[Network architecture](networking.md)
