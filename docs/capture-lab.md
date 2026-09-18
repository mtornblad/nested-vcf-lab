# Deploy a captured lab

The Automation component has one Build Tools project containing six blueprints:
Full Stack VCF, the four Nested VCF Modular catalog items, and
**Full Stack VCF - Capture**. The vRO workflows/classes share the usual
`components/vro-typescript/src/lab` folders. Existing modular workflow and
blueprint names are preserved.

## Prepare and publish

Initialize the pinned submodules, install the normal
[build-host prerequisites](build-host.md), and use the configured Maven profile:

```bash
git submodule update --init --recursive
python3 -m pip install -r components/vcf-automation/requirements-dev.txt
./orchestration/run_automation.py test
./orchestration/run_vro.py validate
./orchestration/run_vro.py upload
./orchestration/run_automation.py upload
```

Publish vRO first because the shared custom-resource definitions reference its
workflow IDs. Capture itself does not run those custom resources. Both upload
commands build before publishing. `--profile` remains available as an override
to the private umbrella settings; no `--variant modular` selection is needed.
Old variant settings are accepted with a notice and use the combined package.
Pull/download also export the complete selection.

Release and request **Full Stack VCF - Capture** from the catalog. It creates a
new namespace, VPC, external IP, NAT and VLAN/trunk network, then deploys the
captured images. It does not run fresh guest bootstrap or scripted VCF bring-up.
See the [component Capture guide](https://github.com/mtornblad/nested-vcf-automation/blob/main/docs/capture.md)
for image IDs, inputs, disk handling and the first deployment checks.

The captures must be complete and available to the new namespace. Verify that
the nested ESXi images include their vSAN disks/data. Guest names, addresses,
credentials and MAC associations are inherited; changing the outer lab name
does not reconfigure them. The host list can vary in length but does not resize
a preconfigured nested cluster.

## REST through the lab proxy

The vRO package includes **se.advania.rest.request**, a Python 3.10 action with
SOCKS5/SOCKS5h support, structured HTTP results, exit codes, timing and controlled
logging. Bind it as an action element in a workflow. The existing Installer
workflows are not automatically switched to it.

Use a proxy reachable from the action runtime and `socks5h` for DNS resolution
inside the private lab. A laptop's loopback SSH tunnel is not automatically
reachable by vRO. Follow the [REST action guide](https://github.com/mtornblad/nested-vcf-orchestrator/blob/main/docs/rest-action.md)
for parameters, output fields, error codes and examples.

[Documentation index](index.md) · [Modular vRO flow](modular-vro.md) ·
[Build and publish](build-workflows.md)
