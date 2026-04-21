# Network Guide: TP-Link TL-SG108E VLAN Configuration

**Last Updated:** 2026-04-10
**Upstream Config:** MikroTik RB2011 ([mikrotik-setup-commands.rsc](../../../infrastructure/mikrotik-setup-commands.rsc))
**Canonical Topology:** [Network_Topology.md](../../../infrastructure/Network_Topology.md)

This guide configures the TP-Link TL-SG108E as a VLAN-aware access switch, trunked to the MikroTik RB2011 which handles inter-VLAN routing, DHCP, NAT, and firewall rules.

## VLAN Overview

| VLAN ID | Name | Subnet | Gateway | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| 10 | MGMT | 10.10.10.0/24 | 10.10.10.1 | Infrastructure management (Proxmox GUI, Switch, NullClaw, RPi services) |
| 20 | GRID | 10.20.20.0/24 | 10.20.20.1 | TrafficGrid workloads (Control Plane, Workers) |
| 30 | TRUSTED_WIFI | 10.30.30.0/24 | 10.30.30.1 | Personal devices via WiFi AP (laptops, phones) |

> VLAN 30 is carried on MikroTik ETH3 to the WiFi AP, **not** through the switch.

## Switch Port Assignment

| Port | Device | VLAN Membership | PVID | Tagging | Description |
| :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | MikroTik RB2011 ETH2 | 10, 20 | 1 | Tagged | Trunk uplink |
| 2 | Minisforum UM680 | 20 | 20 | Untagged | TrafficGrid Control Plane |
| 3 | HP Z420 (Proxmox) | 10 | 10 | Untagged | Worker Plane / Proxmox GUI |
| 4 | MeLE Quieter3Q | 10 | 10 | Untagged | NullClaw / Monitoring |
| 5 | Raspberry Pi 5 | 10 | 10 | Untagged | PhotoPrism / Syncthing |
| 6 | Spare | - | 1 | - | - |
| 7 | Spare | - | 1 | - | - |
| 8 | Spare | - | 1 | - | - |

## Step-by-Step Configuration

### Prerequisites
- TP-Link TL-SG108E in factory default state
- Disconnect the trunk cable to MikroTik before starting (configure switch in isolation)

### 1. Access the Management Interface
Connect your machine to any switch port, then set a static IP:

```bash
sudo ip addr flush dev <interface>
sudo ip addr add 192.168.0.2/24 dev <interface>
sudo ip link set <interface> up
```

- Open `http://192.168.0.1` in a browser
- Login: `admin` / `admin`

### 2. Enable 802.1Q VLAN
- Go to **VLAN** > **802.1Q VLAN**
- Set **802.1Q VLAN Configuration** to **Enable**

### 3. Create VLANs

**VLAN 10 (MGMT):**
- VLAN ID: `10`
- Member Ports: **1** (Tagged), **3** (Untagged), **4** (Untagged), **5** (Untagged)

**VLAN 20 (GRID):**
- VLAN ID: `20`
- Member Ports: **1** (Tagged), **2** (Untagged)

### 4. Configure PVID (Port VLAN ID)
Go to **VLAN** > **802.1Q PVID Setting**:

| Port | PVID |
| :--- | :--- |
| 1 | 1 (default, trunk port) |
| 2 | 20 |
| 3 | 10 |
| 4 | 10 |
| 5 | 10 |

### 5. (Optional) Set Switch Management IP
After VLANs are active, change the switch management IP to `10.10.10.2` (VLAN 10) so it's reachable from the MGMT network:
- Go to **System** > **IP Setting**
- Set IP: `10.10.10.2`, Mask: `255.255.255.0`, Gateway: `10.10.10.1`

### 6. Save and Reconnect
- **Save** the configuration
- Move your machine cable to its assigned port (Port 2 for UM680)
- Connect MikroTik ETH2 to switch Port 1 (trunk)
- Restart networking on your machine:

```bash
sudo ip addr flush dev <interface>
sudo dhclient <interface>
```

### Troubleshooting: OpenSUSE / broken wicked (UM680)

The Minisforum UM680 runs OpenSUSE where `wicked` (the default network manager) is non-functional.
`busybox-static udhcpc` obtains a lease but does **not** apply it (no default script to set IP/route).

**Manual workaround (interface: `eno1`):**

```bash
sudo ip link set eno1 up
sudo ip addr flush dev eno1
sudo busybox-static udhcpc -i eno1          # gets lease but won't apply
sudo ip addr add 10.20.20.200/24 dev eno1    # apply IP manually
sudo ip route add default via 10.20.20.1 dev eno1
```

**Note:** After a full reboot, the UM680 successfully obtains its DHCP lease (10.20.20.200) automatically. The manual workaround above is only needed if networking is reset mid-session.

## Verification

After reconnecting through the trunk:

```bash
# Should get an IP in the correct VLAN subnet
ip addr show <interface>

# Port 2 (UM680) should get 10.20.20.x
# Port 3 (HP) should get 10.10.10.x
# Port 4 (MeLE) should get 10.10.10.x
# Port 5 (RPi) should get 10.10.10.x

# Test gateway reachability
ping 10.20.20.1   # from VLAN 20
ping 10.10.10.1   # from VLAN 10

# Test internet
ping 1.1.1.1
```

## Security Model
- Devices on **VLAN 20 (GRID)** cannot communicate with **VLAN 10 (MGMT)** or **VLAN 30 (TRUSTED)** -- blocked by MikroTik firewall rules
- If a TrafficGrid worker is compromised, it cannot reach Proxmox, the RPi, or personal devices
- VLAN 30 (personal laptops/phones) is entirely on the WiFi AP, physically separate from the switch
