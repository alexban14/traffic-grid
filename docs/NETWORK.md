# TrafficGrid Network Requirements

To run the TrafficGrid infrastructure (EliteMini + Worker nodes), the network must support VLAN-based isolation.

## Current Architecture
- **Gateway:** MikroTik RB2011
- **Switch:** TP-Link SG108E (Managed)
- **VLAN 20 (GRID):** Isolated network for production containers and workers.

## Infrastructure Setup
For detailed configuration of the gateway and switch, refer to the global infrastructure docs in the `brainstorms` repository:
`brainstorms/infrastructure/mikrotik-comprehensive-setup.md`

## Quick Access Configuration
A RouterOS script is available at `brainstorms/infrastructure/mikrotik-setup-commands.rsc` for disaster recovery.
