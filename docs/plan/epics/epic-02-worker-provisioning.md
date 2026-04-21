# Epic 02 — Worker Plane Provisioning

**Goal:** Configure the HP Z420 Proxmox environment and develop the automated LXC worker deployment script.

**Estimated Duration:** 1 week
**Status:** IN PROGRESS — first worker operational, scaling not yet automated

---

## Task Summary

| ID | Title | Status | Notes |
|----|-------|--------|-------|
| E02-T01 | Proxmox Setup | Done | HP Z420 running Proxmox VE (Debian 12, kernel 6.8.12-4-pve), on VLAN 10 (10.10.10.104) |
| E02-T02 | Base Worker Template | Done | `tg-worker-01` LXC (Debian 12, 10.10.10.106) — Chrome 147, Playwright 1.58, Python 3.12 venv |
| E02-T03 | Worker Agent | Done | Celery worker as systemd service, connects to UM680 Redis across VLANs, picks up tasks |
| E02-T04 | Scaling Script | Not Started | Need script to clone N containers from tg-worker-01 template |
| E02-T05 | Proxy Integration | Not Started | Waiting for MeLE proxy gateway setup |

## Implementation Details

### Ansible Automation
- **`ansible/playbooks/setup-worker.yml`** — full provisioning: apt deps, Chrome, Python venv, Playwright browsers, systemd service, code sync
- **`ansible/playbooks/deploy-code.yml`** — fast code-only sync + service restart
- **`ansible/inventory.yml`** — inventory with SSH key auth (`~/.ssh/keys/proxmox-tg-cts`)
- **`ansible/group_vars/all/secrets.yml`** — vault-ready credentials (DB + Redis passwords)

### Network
- Worker on VLAN 10 (10.10.10.106) reaches UM680 on VLAN 20 (10.20.20.200) via MikroTik routing
- MikroTik firewall rule allows UM680 → MGMT VLAN for control plane access
- DNS: `nameserver 1.1.1.1` (Tailscale default doesn't work inside LXC)

### Verified
- Worker registers with Celery, syncs with Docker worker ("mingle: sync with 1 nodes")
- Task dispatched from API → picked up by LXC worker → Playwright executed → result written to DB
