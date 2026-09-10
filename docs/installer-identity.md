# VCF Installer and SDDC Manager identities

The current Full Stack blueprint deploys VCF Installer in the outer Supervisor
namespace. Its JSON requests a new SDDC Manager in the nested environment
(`useExistingDeployment: false`). For that separate-appliance workflow, give
the requested target its own DNS name and address.

| Role | Reference FQDN | Reference address | Source |
| --- | --- | --- | --- |
| VCF Installer | `mtvcf-installer.dclab.se` | `172.16.1.10` | `installer_settings` |
| New SDDC Manager | `mtsddcm01.dclab.se` | `172.16.1.207` | `vcf_settings.sddc_manager` |

Both have A and PTR records in the supplemental VyOS configuration. The
installer vApp hostname uses `installer_settings.fqdn`, while the generated
JSON uses `vcf_settings.sddc_manager.fqdn` for `sddcManagerSpec.hostname`.
The SDDC Manager address is reserved through DNS, not passed as an invented
`ipAddress` property in that API object.

The previous blueprint pointed `sddcManagerSpec.hostname` at the installer
while still requesting a new deployment. This is an inconsistent target for
the separate-appliance workflow and has been corrected. Without the exact
validation error, it does not prove that this was the only reported collision.
The API describes `useExistingDeployment` as the choice between importing an
existing deployment and creating one:
[SddcManagerSpec](https://developer.broadcom.com/xapis/vcf-installer-api/latest/data-structures/SddcManagerSpec/).

## Distinguish the failure before renaming anything

| Observation | Check |
| --- | --- |
| Target already exists or target address responds before new SDDC Manager deployment | Confirm the JSON target is the separate, unused SDDC Manager FQDN and address |
| Reverse lookup returns installer FQDN but validation expects `sddc-manager` | Inspect the installer's own hostname and bootstrap; changing the new SDDC Manager name does not repair the installer OS identity |
| Kubernetes reports `AlreadyExists` | Check the resource name and namespace; this is independent of a DNS FQDN |
| VCF reports a duplicate `sddcId` or instance name | Check that specific inventory identifier; it is independent of `sddcManagerSpec.hostname` |

In the current lab the JSON defaults remain `sddcId: mgmt` and
`vcfInstanceName: vcf`. Independent isolated installations can reuse those
labels. Use distinct identifiers when adding instances/domains to an existing
shared inventory and verify the exact error before changing them.

## Read-only checks

On the installer:

```bash
hostnamectl --static
hostname -f
ip -4 address
getent hosts mtvcf-installer.dclab.se
```

Check DNS from a machine using the VyOS resolver (install `dnsutils` on Ubuntu
if necessary):

```bash
dig @172.16.0.2 mtvcf-installer.dclab.se A +short
dig @172.16.0.2 -x 172.16.1.10 +short
dig @172.16.0.2 mtsddcm01.dclab.se A +short
dig @172.16.0.2 -x 172.16.1.207 +short
dig @172.16.0.2 vis-appliance.dclab.se A +short
```

Inspect only the identity fields in the rendered JSON without printing its
passwords:

```bash
python3 - /tmp/vcf-deployment.json <<'PY'
import json
import sys
from pathlib import Path

spec = json.loads(Path(sys.argv[1]).read_text())
sddc = spec.get("sddcManagerSpec", {})
print(json.dumps({
    "vcfInstanceName": spec.get("vcfInstanceName"),
    "sddcId": spec.get("sddcId"),
    "sddcManagerHostname": sddc.get("hostname"),
    "useExistingDeployment": sddc.get("useExistingDeployment"),
}, indent=2))
PY
```

Inspect the installer's `/var/log/vmware/vcf/domainmanager/domainmanager.log`
around the failed validation. Share the specific error and identity checks;
avoid copying an entire deployment-specification log containing credentials.
If an already deployed installer still calls itself `sddc-manager`, validate
the bootstrap on a fresh test deployment before changing hostnames and
certificates on an appliance with an active installation.

[VCF Automation blueprint](components/vcf-automation.md) ·
[Network architecture](networking.md) · [Troubleshooting](troubleshooting.md)
