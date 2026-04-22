#!/bin/bash
#
# TrafficGrid LXC Worker Scaling Script
#
# Usage:
#   ./scale-workers.sh <count>        # Scale to N total workers (creates missing ones)
#   ./scale-workers.sh status         # Show all tg-worker containers
#   ./scale-workers.sh destroy <id>   # Destroy a specific worker (e.g., destroy 202)
#
# Clones from tg-worker-01 (VMID 200) on Proxmox HP Z420.
# Then runs Ansible setup to configure each new worker.

set -e

PROXMOX_HOST="root@10.10.10.104"
TEMPLATE_VMID=200
BASE_VMID=201                    # First clone starts at 201
STORAGE="hdd1-1tb"
PVE_SSH_KEY="~/.ssh/keys/proxmox-host"       # Key for Proxmox host
WORKER_SSH_KEY="~/.ssh/keys/proxmox-tg-cts"  # Key for LXC containers
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ANSIBLE_DIR="$(dirname "$SCRIPT_DIR")"
INVENTORY_FILE="$ANSIBLE_DIR/inventory.yml"

ssh_pve() {
    ssh -i "$PVE_SSH_KEY" -o StrictHostKeyChecking=no -o BatchMode=yes "$PROXMOX_HOST" "$@"
}

wait_for_ip() {
    local vmid=$1
    local hostname=$2
    local max_wait=60
    local elapsed=0

    echo "  Waiting for $hostname (VMID $vmid) to get DHCP IP..."
    while [ $elapsed -lt $max_wait ]; do
        # Get IP from Proxmox container interface
        local ip=$(ssh_pve "pct exec $vmid -- ip -4 addr show eth0 2>/dev/null | grep 'inet ' | awk '{print \$2}' | cut -d/ -f1" 2>/dev/null)
        if [ -n "$ip" ] && [ "$ip" != "" ]; then
            echo "  $hostname → $ip"
            echo "$ip"
            return 0
        fi
        sleep 3
        elapsed=$((elapsed + 3))
    done
    echo "  WARNING: $hostname did not get an IP after ${max_wait}s"
    return 1
}

cmd_status() {
    echo "=== TrafficGrid Workers on Proxmox ==="
    ssh_pve "pct list" | grep -E "VMID|tg-worker"
    echo ""
    echo "=== Worker IPs ==="
    for vmid in $(ssh_pve "pct list" | grep "tg-worker" | awk '{print $1}'); do
        local name=$(ssh_pve "pct config $vmid" | grep hostname | awk '{print $2}')
        local ip=$(ssh_pve "pct exec $vmid -- ip -4 addr show eth0 2>/dev/null | grep 'inet ' | awk '{print \$2}' | cut -d/ -f1" 2>/dev/null || echo "unknown")
        local status=$(ssh_pve "pct status $vmid" | awk '{print $2}')
        echo "  $name (VMID $vmid) — $status — $ip"
    done
}

cmd_scale() {
    local target_count=$1

    if [ -z "$target_count" ] || [ "$target_count" -lt 1 ]; then
        echo "Usage: $0 <count>"
        echo "  count = total number of workers (including tg-worker-01)"
        exit 1
    fi

    # Count existing tg-worker containers
    local existing=$(ssh_pve "pct list" | grep -c "tg-worker" || echo 0)
    local to_create=$((target_count - existing))

    if [ "$to_create" -le 0 ]; then
        echo "Already have $existing workers (target: $target_count). Nothing to create."
        cmd_status
        return
    fi

    echo "=== Scaling TrafficGrid Workers ==="
    echo "  Existing: $existing"
    echo "  Target:   $target_count"
    echo "  Creating: $to_create new workers"
    echo ""

    # Find the next available VMID
    local next_vmid=$BASE_VMID
    while ssh_pve "pct status $next_vmid" &>/dev/null; do
        next_vmid=$((next_vmid + 1))
    done

    local new_workers=()

    # Ensure template has a snapshot for cloning (avoids stopping it)
    if ! ssh_pve "pct listsnapshot $TEMPLATE_VMID" 2>/dev/null | grep -q "base"; then
        echo "Creating snapshot 'base' on template (VMID $TEMPLATE_VMID)..."
        ssh_pve "pct snapshot $TEMPLATE_VMID base --description 'Base template for worker cloning'"
    fi

    for i in $(seq 1 $to_create); do
        local vmid=$next_vmid
        local worker_num=$((existing + i))
        local hostname="tg-worker-$(printf '%02d' $worker_num)"

        echo "[$i/$to_create] Creating $hostname (VMID $vmid)..."

        # Clone from template snapshot (linked clone — fast, no need to stop template)
        ssh_pve "pct clone $TEMPLATE_VMID $vmid --hostname $hostname --snapname base" 2>&1

        # Start the container
        ssh_pve "pct start $vmid"
        echo "  Started $hostname"

        new_workers+=("$vmid:$hostname")
        next_vmid=$((next_vmid + 1))
    done

    echo ""
    echo "=== Waiting for DHCP IPs ==="
    sleep 5  # Give containers time to boot

    local worker_ips=()
    for entry in "${new_workers[@]}"; do
        local vmid="${entry%%:*}"
        local hostname="${entry##*:}"
        local ip=$(wait_for_ip "$vmid" "$hostname")
        if [ -n "$ip" ]; then
            worker_ips+=("$hostname:$ip")
        fi
    done

    echo ""
    echo "=== Updating Ansible Inventory ==="
    for entry in "${worker_ips[@]}"; do
        local hostname="${entry%%:*}"
        local ip="${entry##*:}"

        # Check if already in inventory
        if grep -q "$hostname" "$INVENTORY_FILE"; then
            echo "  $hostname already in inventory, updating IP..."
            sed -i "s|$hostname:.*|$hostname:\n          ansible_host: $ip|" "$INVENTORY_FILE"
        else
            echo "  Adding $hostname ($ip) to inventory..."
            # Append to workers group (before the last line of the hosts block)
            sed -i "/tg-worker-01:/a\\        $hostname:\n          ansible_host: $ip" "$INVENTORY_FILE"
        fi
    done

    echo ""
    echo "=== Copying SSH Key to New Workers ==="
    for entry in "${worker_ips[@]}"; do
        local hostname="${entry%%:*}"
        local ip="${entry##*:}"
        echo "  Copying key to $hostname ($ip)..."
        ssh-copy-id -i "$WORKER_SSH_KEY" -o StrictHostKeyChecking=no "root@$ip" 2>/dev/null || true
    done

    echo ""
    echo "=== Running Ansible Setup ==="
    cd "$ANSIBLE_DIR"
    ansible-playbook playbooks/setup-worker.yml --limit "$(echo "${worker_ips[@]}" | tr ' ' '\n' | cut -d: -f1 | tr '\n' ',')"

    echo ""
    echo "=== Scale Complete ==="
    cmd_status
}

cmd_destroy() {
    local vmid=$1
    if [ -z "$vmid" ]; then
        echo "Usage: $0 destroy <VMID>"
        exit 1
    fi

    if [ "$vmid" -eq "$TEMPLATE_VMID" ]; then
        echo "ERROR: Cannot destroy the template (VMID $TEMPLATE_VMID)"
        exit 1
    fi

    local hostname=$(ssh_pve "pct config $vmid 2>/dev/null" | grep hostname | awk '{print $2}')
    if [ -z "$hostname" ]; then
        echo "ERROR: VMID $vmid not found"
        exit 1
    fi

    echo "Destroying $hostname (VMID $vmid)..."
    ssh_pve "pct stop $vmid" 2>/dev/null || true
    ssh_pve "pct destroy $vmid"

    # Remove from inventory
    if grep -q "$hostname" "$INVENTORY_FILE"; then
        sed -i "/$hostname/,+1d" "$INVENTORY_FILE"
        echo "Removed $hostname from Ansible inventory"
    fi

    echo "Done."
}

# --- Main ---
case "${1:-}" in
    status)
        cmd_status
        ;;
    destroy)
        cmd_destroy "$2"
        ;;
    [0-9]*)
        cmd_scale "$1"
        ;;
    *)
        echo "TrafficGrid Worker Scaling"
        echo ""
        echo "Usage:"
        echo "  $0 <count>        Scale to N total workers"
        echo "  $0 status         Show all workers"
        echo "  $0 destroy <VMID> Destroy a worker"
        echo ""
        echo "Examples:"
        echo "  $0 5              Scale to 5 workers (creates 4 new clones)"
        echo "  $0 status         List all tg-worker containers with IPs"
        echo "  $0 destroy 203    Stop and remove tg-worker-03"
        ;;
esac
