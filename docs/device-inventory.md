# TrafficGrid: Physical Device Inventory

## 📱 High-Trust Physical Farm
These devices represent the "Tier 0" trust level. They will be used for account creation, warm-up, and high-value interactions (posting, commenting) where browser-based automation might be detected.

### Device List
1.  **Samsung Galaxy S24 Ultra** (Primary / Modern Flagship)
2.  **Samsung Galaxy A40** (Mid-range / Stable)
3.  **Motorola Moto G40** (Large screen / Good for visual debugging)
4.  **Huawei P10** (Legacy / Good for testing older app versions)

## Network Backbone: TP-Link TL-SG108E
VLAN-aware access switch trunked to the MikroTik RB2011. See [VLAN Config Guide](vlan-config-guide.md) and [Network Topology](../../../infrastructure/Network_Topology.md) for full details.

### Network Segmentation (VLANs)
- **VLAN 10 (MGMT / 10.10.10.0/24):** Infrastructure — no devices connected yet (HP Z420, MeLE, RPi pending migration from PNI switch)
- **VLAN 20 (GRID / 10.20.20.0/24):** TrafficGrid workloads — UM680 active (10.20.20.200)
- **VLAN 30 (TRUSTED / 10.30.30.0/24):** Personal devices via WiFi AP (not on this switch)

> **Note:** Most infrastructure devices are currently on the PNI SW016 unmanaged switch (main home network). Only the UM680 is on the TP-Link/VLAN segment. Devices will be migrated as needed.

### QoS (Quality of Service)
The TL-SG108E supports port-based QoS. Priority can be assigned to the trunk port (Port 1) and the UM680 port (Port 2) to ensure TrafficGrid control traffic is not starved.

### Monitoring
The TL-SG108E supports **Port Mirroring**, which can be used to sniff traffic for debugging blocked requests.

## Physical Device Farm
- **Orchestrator:** The **HP Z420 (Proxmox)** will act as ADB Host (planned — device currently on PNI switch)
- **Control:** `uiautomator2` (Python) or `Appium` for interaction logic
- **Visuals:** `scrcpy` for real-time monitoring of the device farm
- **Networking:** Each device uses its own SIM card (Mobile Data) to provide a unique, high-trust IP exit node

## 🚀 Allocation Table
| Device | Priority | Primary Task |
| :--- | :--- | :--- |
| S24 Ultra | High | High-value account management / Content Posting |
| A40 | Medium | Account Warm-up (Scrolling/Liking) |
| Moto G40 | Medium | Mass Viewing / Interaction Testing |
| P10 | Low | Proxy Exit Node / Legacy App Testing |