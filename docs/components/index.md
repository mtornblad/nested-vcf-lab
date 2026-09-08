# Components

Each component remains independently buildable and owns its internal test and
configuration contract. The umbrella repository pins a compatible set and adds
shared operator workflows around it.

| Component | Source role | Output or runtime role | Maturity in umbrella |
| --- | --- | --- | --- |
| [VyOS OVA Builder](vyos-ova-builder.md) | Custom builder maintained for this project | VMware OVA with vApp first boot | Integrated |
| [VyOS Build](vyos-build.md) | Fork of the VyOS image builder | VMDK consumed by OVA Builder | Integrated dependency |
| [VIS](vis.md) | Infrastructure-service appliance project | Multi-service Ubuntu OVA | Independently buildable |
| [Nested ESXi Packer](nested-esxi.md) | Initial Packer implementation | Nested ESXi OVF/OVA | Experimental |

## Source links

- [mtornblad/vyos-ova-builder](https://github.com/mtornblad/vyos-ova-builder)
- [mtornblad/vyos-build](https://github.com/mtornblad/vyos-build)
- [mtornblad/vcf-infrastructure-service-appliance](https://github.com/mtornblad/vcf-infrastructure-service-appliance)
- [mtornblad/nested-esxi-packer](https://github.com/mtornblad/nested-esxi-packer)

Component commits should be reviewed and pushed in their own repositories
before the umbrella gitlink is advanced. See [Development](../development.md).

[Documentation home](../index.md) · [Architecture](../architecture.md)
