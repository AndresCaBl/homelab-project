# Runbook

## Phase 0 – Repo Bootstrap
- Create private GitHub repo and commit initial scaffold.
- Add `network.yaml` with reserved IPs and MAC addresses for each host.
- Maintain ADRs in `decisions.md` as design decisions evolve.

## Phase 1 – Network Prep
- Connect both laptops via Ethernet through unmanaged switch; Wi-Fi only as fallback.
- Configure DHCP reservations in eero for both Ethernet MACs:
  - `srv-media` → 192.168.4.90
  - `lab-proxmox` → 192.168.4.91
- Disable UPnP in eero for improved security.

## Phase 2 – OS Installs & Base Hardening
- Install Ubuntu Server 22.04 on `srv-media`.
- Install Proxmox VE on `lab-proxmox`.
- Apply baseline hardening:
  - Configure SSH keys for passwordless login.
  - Enable and configure UFW firewall.
  - Apply all system updates.

## Phase 3 – Early Remote Access
- Install and configure Tailscale on both hosts:
  - `srv-media`: Ubuntu Server
  - `lab-proxmox`: Proxmox VE
- Enable **MagicDNS** in Tailscale Admin Console.
- Verify name-based access:
  - SSH: `ssh andres@srv-media`
  - Proxmox UI: `https://lab-proxmox.tail401c13.ts.net:8006`

  ## Phase 4 – Storage Layout & Library Migration
- Mount external USB drives by UUID:
  - `/srv/media/movies` → USB Drive 1 (ext4, UUID mounted with `noatime`)
  - `/srv/media/tv` → USB Drive 2 (ext4, UUID mounted with `noatime`)
- Verify mounts with `findmnt` and confirm `noatime` option active.
- Migrate media libraries from old server using `rsync` for fast LAN transfer.
- Verify transfer with `du -sh` and `find . | wc -l`.
- Normalize permissions:
  - Owner: `andres:andres`
  - Directories: `755`
  - Files: `644`
- Perform initial tidy-up
- Final folder tree after mounting USB drives and cache drive
    /srv/
    ├── backup
    │   ├── configs
    │   └── db_dumps
    ├── bin
    ├── cache
    │   └── downloads
    │       ├── incomplete
    │       ├── seeding
    │       └── watch
    ├── compose
    │   ├── download-stack
    │   └── media-stack
    ├── config
    │   ├── bazarr
    │   ├── gluetun
    │   ├── jellyfin
    │   ├── overseerr
    │   ├── prowlarr
    │   ├── radarr
    │   └── sonarr
    └── media
        ├── movies
        └── tv

