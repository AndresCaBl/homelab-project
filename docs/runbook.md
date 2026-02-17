# Runbook

This runbook captures the major build phases and the current operating model.
Authoritative current state: `docs/ipam.md` (addressing/DNS), `docs/decisions.md` (ADRs).

---

## Phase 0 — Repo bootstrap

- Create repo scaffold (`docs/`, `compose/`, `config/`, `bin/`, `backup/`).
- Record decisions in `docs/decisions.md`.
- Track addressing and naming in `docs/ipam.md`.

---

## Phase 1 — Initial network (historical)

- Hosts connected via Ethernet through an unmanaged switch.
- eero provided routing/DHCP on `192.168.4.0/22`.
- DHCP reservations:
  - `srv-media` → `192.168.4.90`
  - `lab-proxmox` → `192.168.4.91` (later removed)
- UPnP disabled on eero.

---

## Phase 2 — Current network (UniFi + VLANs)

- UniFi UXG-Lite is the gateway/firewall.
- VLANs and subnets are defined in `docs/ipam.md`.
- `srv-network.home.arpa` runs:
  - UniFi Network Application (Docker)
  - Pi-hole (Docker)
- DHCP is enabled for Clients VLAN only (initially). Infra/Servers use static/reservations.

---

## Phase 3 — OS baseline and host hardening

- `srv-media`: Ubuntu Server 24.04.3 LTS
- Baseline:
  - SSH key-based auth
  - UFW enabled (rules documented with the service that requires them)
  - System updates applied

Removed:
- `lab-proxmox` (decommissioned)

---

## Phase 4 — Remote access

- Tailscale installed on `srv-network` and `srv-media`.
- MagicDNS enabled.

---

## Phase 5 — Storage layout and migration

- USB drives mounted by UUID with `noatime`:
  - `/srv/media/movies`
  - `/srv/media/tv`
- SSD cache paths:
  - `/srv/cache/downloads/{incomplete,seeding,watch}`
  - `/srv/cache/transcodes`
- Media migration performed over LAN using `rsync`.
- Verification:
  - `findmnt` confirms mounts and `noatime`
  - `du -sh` and `find . | wc -l` used for rough parity checks
- Permissions:
  - owner `andres:andres`
  - directories `755`
  - files `644`

`/srv` layout (current intent):

/srv/
├── backup/
│   ├── configs/
│   └── db_dumps/
├── bin/
├── cache/
│   ├── downloads/
│   │   ├── complete/
│   │   ├── incomplete/
│   │   └── watch/
│   └── transcodes/
├── compose/
│   ├── download-stack/
│   └── media-stack/
├── config/
│   ├── bazarr/
│   ├── gluetun/
│   ├── homepage/
│   ├── jellyfin/
│   ├── jellyseerr/
│   ├── plex/
│   ├── prowlarr/
│   ├── qbittorrent/
│   ├── radarr/
│   └── sonarr/
└── media/
    ├── movies/
    └── tv/

Notes:
- `overseerr` removed (replaced by Jellyseerr).
- Cache uses `incomeplte/` to match the seeding strategy.

---

## Phase 6 — Docker and Compose conventions

- Compose projects under `/srv/compose`:
  - `download-stack` (Gluetun, qBittorrent, Prowlarr, FlareSolverr)
  - `media-stack` (Plex, Jellyfin, Sonarr, Radarr, Bazarr, Jellyseerr)
- Conventions:
  - Each stack has a `.env` and committed `.env.example`. Shared values live in `compose/_shared/.env`.
  - Persistent paths map to `/srv`:
    - configs → `/srv/config/<service>`
    - media → `/srv/media`
    - cache/downloads → `/srv/cache`
  - Images may use `:latest` during iteration; pin versions/digests when stable.
  - Health checks are simple endpoints per service.

Operational commands:
- Render config: `docker compose -f /srv/compose/<stack>/docker-compose.yml config`
- Start one service: `docker compose -f /srv/compose/<stack>/docker-compose.yml up -d --no-deps <service>`
- Health status: `docker inspect -f '{{.State.Health.Status}}' <container>`

---

## Phase 7 — VPN download stack (Gluetun + qBittorrent + Prowlarr + FlareSolverr)

- `qbittorrent`, `prowlarr`, `flaresolverr` run with `network_mode: service:gluetun`.
- Published via Gluetun:
  - qBittorrent WebUI → `${QBITTORRENT_WEBUI_PORT}:8080`
  - Prowlarr WebUI → `${PROWLARR_WEBUI_PORT}:9696`
  - FlareSolverr → `8191:8191`
  - Gluetun control → `8000:8000` (local status)

Paths:
- qBittorrent:
  - `/config` → `/srv/config/qbittorrent`
  - `/downloads` → `/srv/cache/downloads`
- Prowlarr:
  - `/config` → `/srv/config/prowlarr`

Service endpoints (from other containers):
- qBittorrent: `http://gluetun:8080`
- FlareSolverr: `http://flaresolverr:8191`

Verification:
- Gluetun health: `docker inspect -f '{{.State.Health.Status}}' gluetun`
- qBittorrent: `curl -fsS http://localhost:8080/api/v2/app/version`
- FlareSolverr: `curl -fsS http://localhost:8191/health`
- VPN egress IP (inside Gluetun): `docker exec -it gluetun sh -c 'wget -qO- https://ipinfo.io/ip'`

---

## Phase 8 — Media apps (Plex-first) and automation

Primary frontend:
- Plex (primary)

Secondary:
- Jellyfin (deployed, not the default)

Service URLs (use hostnames, not IP literals):
- Plex: http://srv-media.home.arpa:32400/web (`/identity`)
- Jellyfin: http://srv-media.home.arpa:8096 (`/health`)
- Sonarr: http://srv-media.home.arpa:8989 (`/ping`)
- Radarr: http://srv-media.home.arpa:7878 (`/ping`)
- Bazarr: http://srv-media.home.arpa:6767
- Jellyseerr: http://srv-media.home.arpa:5055
- qBittorrent (via Gluetun): http://srv-media.home.arpa:8080
- Prowlarr (via Gluetun): http://srv-media.home.arpa:9696
- FlareSolverr (via Gluetun): http://srv-media.home.arpa:8191

Sonarr/Radarr integration:
- Download client: qBittorrent via `http://gluetun:8080`
- Hardlinks off; copy-on-import to keep seeding on SSD and libraries on USB.

Quality size caps (MB/min):
- Movies (1080p WEB): preferred ~20–22; max ~35–36
- TV (1080p WEB): preferred ~16; max ~26

Subtitles:
- Sonarr/Radarr import existing subtitles.
- Bazarr fetches missing/additional only.

Requests:
- Jellyseerr is the requests app. Authentication is via Jellyfin accounts.

---

## Phase 9 — Ops (Cockpit on srv-media)

- Cockpit on `srv-media`:
  - URL: https://srv-media.home.arpa:9090
- Packages installed (recorded for rebuild parity):
  sudo apt install -y cockpit cockpit-packagekit network-manager cockpit-networkmanager \
                     pcp pcp-zeroconf cockpit-pcp smartmontools nvme-cli lm-sensors
  sudo systemctl enable --now cockpit.socket pmcd pmlogger pmproxy

Network renderer (srv-media):
- Netplan uses NetworkManager:
  network:
    version: 2
    renderer: NetworkManager
    ethernets:
      enp0s31f6:
        dhcp4: true

CLI checks:
- `pkcon refresh force`
- `pmstat -t 1 -s 5`
- `pmiostat -t 1 -s 5`
- `sensors`

Needs cleanup:
- Update any UFW rules that still reference `192.168.4.0/22` to match current VLAN subnets (`10.10.0.0/16` scope) and the intended access model.
