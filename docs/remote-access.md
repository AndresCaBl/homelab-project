# Phase 3 – Early Remote Access

## Objective
Enable secure remote access to both homelab hosts (`srv-media` and `lab-proxmox`) without relying on router port forwarding.

## Tailscale Setup

### 1. Installation (Linux: Ubuntu/Proxmox)

    curl -fsSL https://tailscale.com/install.sh | sh
    sudo systemctl enable --now tailscaled
    sudo tailscale up

- Check assigned Tailscale IP:

    tailscale ip -4

### 2. MagicDNS

Enabled via Tailscale Admin Console → DNS → Enable MagicDNS.

Allows access using hostnames instead of IPs:

    srv-media.tail401c13.ts.net

    lab-proxmox.tail401c13.ts.net


    ping srv-media
    ping lab-proxmox


