# Runbook

## Phase 0 (this repo)
- Create private repo and commit initial scaffold.
- Fill `docs/network.yaml` with real IPs/MACs when available.
- Keep ADRs in `docs/decisions.md` up to date.

## Phase 1 – Network Prep
- Wire Ethernet-first via unmanaged switch; keep Wi‑Fi fallback.
- Confirm DHCP reservations in eero; disable UPnP.

## Phase 2 – OS Installs & Base Hardening
- Ubuntu Server 22.04 on srv-media; Proxmox on lab-proxmox.
- Configure SSH keys, UFW, updates.
