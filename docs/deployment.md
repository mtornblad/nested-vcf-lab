# Deployment and first boot

The build workflow ends with a reusable OVA. Deployment automation selects the
runtime network, provides vApp values, and creates a VM from the Content Library
item. This separation keeps lab-specific addresses and secrets out of the OVA.

## Publish the OVA

Validate the upload contract before importing:

```bash
./orchestration/run_vyos.py validate-upload
./orchestration/run_vyos.py upload
```

The adapter calls `govc library.import` using the configured vCenter, Content
Library, and template name. Confirm that `GOVC_URL` resolves to vCenter itself:

```bash
govc about
govc library.ls
```

## Discover the VM Operator image

After the Content Library has synchronized with Supervisor:

```bash
kubectl get clustervirtualmachineimage
kubectl get clustervirtualmachineimage <image-name> \
  -o jsonpath='{range .status.ovfProperties[*]}{.key}{"\n"}{end}'
```

Use the property IDs reported by the image object. VMware Tools exposes the
qualified values inside VyOS as `guestinfo.<property>`.

## Minimal VM Operator bootstrap

The API version and class names are platform-dependent. The important part of
the manifest is the contract, not the literal sample values:

```yaml
spec:
  className: best-effort-medium
  imageName: <cluster-virtual-machine-image>
  powerState: PoweredOn
  storageClass: <storage-class>
  network:
    interfaces:
      - name: management
        network:
          apiVersion: crd.nsx.vmware.com/v1alpha1
          kind: Subnet
          name: uplink
      - name: trunk
        network:
          apiVersion: crd.nsx.vmware.com/v1alpha1
          kind: Subnet
          name: trunk
  bootstrap:
    vAppConfig:
      properties:
        - key: hostname
          value:
            value: lab-router
        - key: ipaddress
          value:
            value: 172.16.0.2
        - key: netmask
          value:
            value: "24"
        - key: gateway
          value:
            value: 172.16.0.1
        - key: management_network
          value:
            value: uplink
        - key: trunk_network
          value:
            value: trunk
        - key: enable_ssh
          value:
            value: "true"
        - key: config_base64
          value:
            value: <base64-encoded-set-and-delete-commands>
```

Supply password and API-key properties from a secret-aware deployment input.
Do not commit them in a blueprint default.

## OVF environment transport

The OVA builder adds the VMware Tools transport to the OVF:

```text
com.vmware.guestInfo
```

For a Supervisor-managed VM, inventory paths may not be browsable like a
normal vCenter folder. Resolve its managed object ID and query that directly:

```bash
VM_OBJECT=$(govc find -i / -type m -name '<vm-name>')
printf '%s\n' "$VM_OBJECT"

govc object.collect -s "$VM_OBJECT" guest.toolsRunningStatus
govc object.collect -s "$VM_OBJECT" \
  config.vAppConfig.ovfEnvironmentTransport
```

Expected results are `guestToolsRunning` and `com.vmware.guestInfo`.

## Guest-side verification

```bash
sudo systemctl status open-vm-tools.service --no-pager -l
vmtoolsd --cmd 'info-get guestinfo.ovfEnv'
sudo grep -F 'vyos-vapp-init' /var/log/messages | tail -n 100
sudo test -e /opt/vyos-ova-builder/vapp-configured \
  && echo 'configuration complete' \
  || echo 'configuration incomplete'
```

The VyOS post-configuration hook runs `/usr/local/sbin/vyos-vapp-init`. On
success it performs one `commit`, one `save`, normalizes configuration archive
permissions, and creates the completion marker. On failure it leaves the marker
absent so the next boot retries.

## Network verification

```bash
show interfaces
show ip route
show nat source rules
show configuration commands | match 'service ssh|service https'
```

Confirm the management and trunk networks by MAC mapping rather than by their
observed `eth` numbers. See [Network architecture](networking.md).

## Blueprint ownership

**Current:** the complete CCI deployment blueprint is maintained outside the
umbrella repository.

**Target:** reusable blueprints should be versioned below a dedicated
deployment directory, split into tested modules for namespace/VPC, networks,
VyOS, ESXi hosts, installer, and optional access hosts. Host lists, IP pools,
DNS/NTP settings, and passwords must be inputs or structured variables rather
than repeated literals.

[Configuration](configuration.md) · [VyOS OVA Builder](components/vyos-ova-builder.md) ·
[Troubleshooting](troubleshooting.md)
