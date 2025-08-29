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
- **Update:** `srv-media` is **Ubuntu Server 24.04.3 LTS** (not 22.04).
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
    │       ├── complete
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
## Phase 5 – Docker & Compose

- Create two stacks under `/srv/compose`:
  - `download-stack` (Gluetun, qBittorrent, Prowlarr, FlareSolverr)
  - `media-stack` (Jellyfin, Plex, Sonarr, Radarr, Bazarr, Jellyseerr)
- Compose conventions:
  - Each stack has its own `.env` and committed `.env.example`; shared values live in `compose/_shared/.env`
    (e.g., `PUID=1000`, `PGID=1000`, `TZ`, `CONFIG_ROOT`, `MEDIA_ROOT`, `CACHE_ROOT`, `LAN_NETWORK`, `FIREWALL_OUTBOUND_SUBNETS`).
  - Volumes map to `/srv`:
    - Configs → `/srv/config/<service>`
    - Media → `/srv/media` (read-only for servers)
    - Downloads/Cache → `/srv/cache` (`/srv/cache/downloads/{incomplete,complete,watch}`, `/srv/cache/transcodes`)
  - Use `:latest` images during build-out; **pin digests later**.
  - Healthchecks: simple HTTP checks per service (added across Phases 6–7).
  - External Docker network `homelab` for services needing fixed IP/peer discovery.
- Useful commands:
  - Render composed config: `docker compose -f compose/<stack>/docker-compose.yml config`
  - Start one service: `docker compose -f compose/<stack>/docker-compose.yml up -d --no-deps <service>`
  - Check health: `docker inspect -f '{{.State.Health.Status}}' <container>`

## Phase 6 – VPN Download Stack (Gluetun + qBittorrent + Prowlarr + FlareSolverr)

- Gluetun (PIA) safety defaults:
  - Kill switch firewall: `FIREWALL=on`
  - DNS-over-TLS: `DOT=on`
  - Port forwarding: `VPN_PORT_FORWARDING=on` with post-hook to set qBittorrent listen port via WebUI API
  - LAN/bridge egress: `FIREWALL_OUTBOUND_SUBNETS=192.168.4.0/22,172.18.0.0/16,172.19.0.0/16`
  - Control server: `HTTP_CONTROL_SERVER=on`, exposed on `8000` (local status only)
- Network model:
  - `qbittorrent`, `prowlarr`, `flaresolverr` run with `network_mode: service:gluetun` (all traffic via VPN).
  - Host ports (published via Gluetun):
    - qBittorrent WebUI → `${QBITTORRENT_WEBUI_PORT}:8080`
    - Prowlarr WebUI → `${PROWLARR_WEBUI_PORT}:9696`
    - FlareSolverr API → `8191:8191`
    - Gluetun control → `8000:8000`
- Paths & storage:
  - qBittorrent:
    - `/config` → `/srv/config/qbittorrent`
    - `/downloads` → `/srv/cache/downloads` (SSD; keeps seeding fast)
  - Prowlarr: `/srv/config/prowlarr`
  - FlareSolverr: runs behind Gluetun; defaults are sufficient
- App linkage (used by Sonarr/Radarr in Phase 7):
  - qBittorrent endpoint (from apps): `http://gluetun:8080`
  - FlareSolverr endpoint (from Prowlarr): `http://flaresolverr:8191`
- Safety/quality:
  - qBittorrent banned file types block executables/scripts/archives/docs; keep `*sample.*` blocked.
- Health & verification:
  - Gluetun health: `docker inspect -f '{{.State.Health.Status}}' gluetun`
  - qBittorrent health: `curl -fsS http://localhost:8080/api/v2/app/version` (from container namespace)
  - Prowlarr health: `curl -fsS http://localhost:9696/` (from container namespace)
  - FlareSolverr health: `curl -fsS http://localhost:8191/health` (from container namespace)
  - Confirm VPN egress IP (inside Gluetun): `docker exec -it gluetun sh -c 'wget -qO- https://ipinfo.io/ip'`
  - Confirm forwarded listen port applied (check Gluetun logs and qBittorrent Connection settings)

## Phase 7 – Media Apps & File Renaming

- **Scope:** Deploy and configure Jellyfin, Plex, Sonarr, Radarr, Bazarr, and Jellyseerr; implement naming/size policies; requests flow; healthchecks.

### Jellyfin (primary frontend)

- **First run:**
  - URL: `http://192.168.4.90:8096` (or Tailscale/MagicDNS hostname).
  - Create admin, add libraries: Movies → `/media/movies`, TV → `/media/tv`.

- **Transcoding (Intel VAAPI on Comet Lake UHD):**
  - `Dashboard → Playback → Hardware acceleration`: **VAAPI**.
  - Enable hardware decoding for **H.264**, **HEVC**, **MPEG2**, **VP9**; enable **10-bit** decode for HEVC/VP9 if you play those.
  - Leave hardware encoding **off** unless needed; Jellyfin’s VAAPI encode works, but decode is the big win.
  - Transcodes path: `/transcode` → `/srv/cache/transcodes` (SSD).

- **Networking & access:**
  - Local only (LAN + Tailscale). Do **not** enable public remote access.
  - Allow lists used: `192.168.4.0/22` and Tailscale CGNAT ranges.

- **Library scans:**
  - After file moves/renames: `Dashboard → Scheduled Tasks → Scan media library`.
  - Per-library: `Library → Three dots → Scan`.

### Plex (dual-use frontend)

- **First run / claim:**
  - URL: `http://192.168.4.90:32400/web` → sign in; server claimed (token stored in Preferences).
  - `ADVERTISE_IP=http://192.168.4.90:32400/` set in Compose for discovery.

- **Transcoding:**
  - If Plex Pass: enable **Hardware Transcoder**. Path `/transcode` → `/srv/cache/transcodes`.
  - Libraries point to `/media/movies` and `/media/tv` (read-only).

- **Access:**
  - LAN + Tailscale only; no WAN port forwarding. Managed users can sign in via app once server visible on LAN.

### Sonarr & Radarr (automation + renaming)

- **Service URLs:**
  - Sonarr: `http://192.168.4.90:8989`
  - Radarr: `http://192.168.4.90:7878`

- **Download client:**
  - qBittorrent via Gluetun: `http://gluetun:8080`.
  - Paths mounted identically on apps and qBittorrent: `/downloads` → `/srv/cache/downloads`.
  - **Remote Path Mapping:** not required (local and remote paths match).

- **Media Management (both):**
  - **Rename = On** (standard formats).
  - **Import Subtitle Files = On**; **Import Extra Files = Off**.
  - **Analyze video files = On**; **Completed Download Handling = On**.
  - **Use hardlinks instead of copy = Off** (copy from SSD to library for continued seeding).
  - **Minimum Free Space**: 5–10 GB.

- **Quality size caps (MB/min):**
  - **Movies (WEB 1080p):** Preferred ~**20–22**; Max ~**35–36**.
  - **TV (WEB 1080p):** Preferred ~**16**; Max ~**26**.
  - Adjust other tiers proportionally inside profiles.

- **Custom Formats / Scoring:**
  - **Movies:** `YTS +600`, `Freeleech +250`.
  - **TV:** `Freeleech +200–300`.
  - Ensure these CFs are attached to the active quality profiles; quality order still applies.

### Bazarr (subtitles)

- **Service URL:** `http://192.168.4.90:6767`
- **Connections:** Link to Sonarr and Radarr (Settings → Sonarr/Radarr).
- **Languages:** English (+ Spanish).
- **Providers:** OpenSubtitles + YIFY Subtitles configured.
- **Policy:** Keep *embedded* subs from Sonarr/Radarr imports; Bazarr fetches **missing/additional** only.

### Jellyseerr (requests)

- **Service URL:** `http://192.168.4.90:5055`
- **Auth:** Connect to **Jellyfin**; family members sign in with Jellyfin accounts.
- **Apps:** Connect Jellyseerr → Sonarr + Radarr; set default root folders (`/media/tv`, `/media/movies`) and quality profiles.
- **Policy:** Auto-approve household; manual approval optional for others.

### Prowlarr (indexers)

- **Sync:** Full-sync indexers to Sonarr/Radarr.
- **Priorities:** Public (e.g., **YTS=1**), other publics 5–8, private indexers ≥30.
- **FlareSolverr:** `http://flaresolverr:8191` for CF-protected indexers.

### qBittorrent (behind Gluetun)

- **Paths:** `/downloads/incomplete`, `/downloads/complete`, `/downloads/watch`.
- **Safety:** Banned file types set (block executables/scripts/archives/docs; keep `*sample.*` blocked).
- **Seeding strategy:** Keep completed data on SSD; Sonarr/Radarr copy to `/media` to continue seeding.

### Healthchecks (Compose)

- **Jellyfin:** `GET /health`
- **Plex:** `GET /identity`
- **Sonarr/Radarr:** `GET /ping`
- **Bazarr:** `GET /`
- **Jellyseerr:** Node HTTP `/`
- **qBittorrent:** `GET /api/v2/app/version`
- **Prowlarr:** `GET /`
- **FlareSolverr:** `GET /health`
- **Gluetun:** built-in healthcheck
