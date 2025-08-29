# Decisions & Rationale (ADR-style summaries)

# Decisions & Rationale (ADR-style summaries)

## ADR-000: Hostnames & IP Plan
- **Context:** Two laptops used as nodes.
- **Decision:** Use `srv-media` (Ubuntu) and `lab-proxmox` (Proxmox) with reserved IPs in 192.168.4.0/24.
- **Status:** Approved
- **Consequences:** Consistent addressing, easy migration.

## ADR-001: Everything under /srv on hosts
- **Context:** Need a predictable directory layout and migration-friendly storage approach.
- **Decision:** Use `/srv/{media,downloads,config,compose,bin,backup}` with UUID-based mounts for USB drives.
- **Status:** Approved
- **Consequences:** Simplifies backup, restore, and migration processes.

## ADR-002: Everything-as-Code via Docker Compose
- **Context:** Consistency across services and environments.
- **Decision:** Each stack has its own compose project and `.env.example` committed (no secrets).
- **Status:** Approved
- **Consequences:** Simplifies deployment and version control for services.

## ADR-003: Repo workflow
- **Context:** Minimize CR/LF issues and path differences between dev and prod environments.
- **Decision:** Use WSL for git and scripting to match Linux hosts.
- **Status:** Approved
- **Consequences:** Avoids cross-platform compatibility issues.

## ADR-004: Timezone & IDs
- **Context:** Consistent timekeeping and permissions across containers and hosts.
- **Decision:** Use `TZ=Australia/Brisbane`, `PUID=1000`, `PGID=1000` for containers.
- **Status:** Approved
- **Consequences:** Ensures logs have correct timestamps and files have consistent ownership.

## ADR-005: IP convention
- **Context:** Predictable network layout for easier troubleshooting and expansion.
- **Decision:** Reserve `.90` (srv-media), `.91` (lab-proxmox), `.92` (Pi-hole LXC).
- **Status:** Approved
- **Consequences:** Simplifies identification and management of lab devices.

## ADR-006: Disable Wi-Fi for lab hosts
- **Context:** Consistent addressing and simpler routing.
- **Decision:** Use Ethernet only (adapters + unmanaged switch).
- **Status:** Approved
- **Consequences:** Reduces network complexity and improves stability.

## ADR-007: IPv4-only for early phases
- **Context:** Reduce complexity; align with early CCNA study.
- **Decision:** Disable IPv6 on Eero and hosts.
- **Status:** Approved
- **Consequences:** Simpler firewall rules, predictable connectivity; IPv6 to be revisited later.

## ADR-008: DHCP reservations on Eero
- **Context:** Predictable addressing for `srv-media` & `lab-proxmox`.
- **Decision:** Reserve 192.168.4.90 and .91 to Ethernet MACs.
- **Status:** Approved
- **Consequences:** Ensures consistent IP allocation.

## ADR-009: OS selection & installation
- **Context:** Need stable, supported base OS for each host’s role.
- **Decision:**
  - `srv-media`: Ubuntu Server 22.04.4 LTS (LTS stability, minimal footprint).
  - `lab-proxmox`: Proxmox VE 8.x (Debian-based hypervisor).
  - `old-dell`: Ubuntu Desktop 24.04 (temporary migration source).
- **Status:** Approved
- **Consequences:** Reliable platforms aligned to each role’s needs.

## ADR-010: SSH key-based authentication as default
- **Context:** Secure, repeatable, and automation-friendly access to all lab nodes.
- **Decision:**
  - Generate single Ed25519 keypair (`homelab_ed25519`) on WSL client.
  - Deploy public key to all hosts (`srv-media`, `lab-proxmox`, `old-dell`).
  - Configure `~/.ssh/config` with host aliases.
  - Enable `ssh-agent` auto-start in WSL to cache keys.
  - Disable SSH password authentication after key verification.
- **Status:** Approved
- **Consequences:** Consistent login experience across lab, improved security, supports automation workflows.

## ADR-0011: Remote Access via Tailscale
- **Status:** Approved
- **Context:** Secure access to homelab services (Ubuntu server and Proxmox) from anywhere without router port forwarding.
- **Decision:** Use Tailscale for mesh VPN connectivity. Enable MagicDNS to allow name-based access (`srv-media`, `lab-proxmox`) instead of Tailscale IPs. Exit Node support is optional, not enabled by default.
- **Consequences:**
  - Devices remain accessible regardless of LAN IP changes.
  - Simplified remote management, similar to Azure Bastion/VPN Gateway.

## ADR-0012: Storage Layout & Library Migration
- **Status:** Approved
- **Context:** Media libraries from old server needed migration into new, migration-friendly `/srv` structure.
- **Decision:**
  - Use `/srv/media/movies` and `/srv/media/tv` as mount points for external drives, mounted by UUID with `noatime`.
  - Migrate existing content via `rsync`.
  - Normalize permissions (owner: andres, dirs 755, files 644).
  - Perform initial tidy-up but defer renaming/duplicates handling to Radarr/Sonarr.
- **Consequences:**
  - Storage layout is consistent and portable.
  - Future migrations only require mounting drives at same `/srv` paths.
  - Old server remains online temporarily as fallback.

  ## ADR-013: Unified /srv Folder Structure with SSD Cache

- **Status:** Approved
- **Context:**
  To support migration-friendly and performance-optimized media management, we need a consistent and predictable `/srv` tree.
  The SSD cache drive handles all torrent activity, while USB HDDs provide long-term storage for movies and TV shows.
  This ensures fast I/O for downloads/seeding and clean separation of persistent data.

- **Decision:**
  - Use `/srv/cache/downloads/{incomplete,seeding,watch}` on the SSD cache drive.
  - Use `/srv/media/movies` and `/srv/media/tv` on USB drives (mounted by UUID with `noatime`).
  - Keep service configs under `/srv/config/<service>`.
  - Keep Compose projects under `/srv/compose/<stack>`.
  - Keep backups under `/srv/backup/{configs,db_dumps}`.

- **Consequences:**
  - Docker containers (qBittorrent, Sonarr, Radarr, etc.) will rely on a consistent path layout.
  - Migration to other hosts (NUC, UnRAID) is simplified by re-using `/srv` layout.
  - Cache SSD prevents excessive writes on USB HDDs, improving performance and longevity.

## ADR-014: Media frontends — Jellyfin primary + Plex dual-use

- **Status:** Approved
- **Context:**
  Need great local UX with flexibility for devices that prefer Plex.
- **Decision:**
  - Run both frontends; Jellyfin is the daily driver, Plex available as secondary.
  - Share libraries at `/media/movies` and `/media/tv`.
  - Use SSD cache at `/transcode`; map `/dev/dri` for hardware acceleration.
- **Consequences:**
  - Broad client compatibility without sacrificing Jellyfin-first workflow.
  - Consistent library paths for both servers.

## ADR-015: Subtitles ownership — import included subs; Bazarr fetches missing only

- **Status:** Approved
- **Context:**
  Many files already include synced subtitles; avoid duplicate or conflicting subs.
- **Decision:**
  - Sonarr/Radarr: `Import Subtitle Files = On`; `Import Extra Files = Off`; renaming On.
  - Bazarr manages only missing/additional subtitles.
- **Consequences:**
  - Preserves embedded, in-sync subs; reduces unnecessary downloads.
  - Jellyfin/Plex read `.srt` files placed alongside media.

## ADR-016: Seeding strategy — Option B (copy on import; hardlinks Off)

- **Status:** Approved
- **Context:**
  Keep torrents seeding from SSD while libraries live on USB storage.
- **Decision:**
  - Completed Download Handling On; Use hardlinks Off.
  - Copy from `/downloads` to `/media` during import.
- **Consequences:**
  - Sustained seeding performance from SSD.
  - Clean, stable library paths on long-term storage.

## ADR-017: Release selection — prefer public (YTS) and freeleech when same quality

- **Status:** Approved
- **Context:**
  Prefer public indexers (YTS for movies) and freeleech options even if slightly larger within limits.
- **Decision:**
  - Custom Formats: `YTS +600` (movies), `Freeleech +250` (movies), `Freeleech +200–300` (TV).
  - Prowlarr priorities: `YTS = 1`, other public indexers `5–8`, private indexers `≥30`; Full Sync to apps.
- **Consequences:**
  - Among same-quality results, YTS/freeleech wins.
  - Quality order still takes precedence unless profile order is adjusted.

## ADR-018: Quality size caps (MB/min) — movies and TV

- **Status:** Approved
- **Context:**
  Keep files lean without penalizing good WEB encodes.
- **Decision:**
  - Movies (1080p WEB): Preferred about **20–22 MB/min**, Max about **35–36 MB/min**.
  - TV (1080p WEB): Preferred about **16 MB/min**, Max about **26 MB/min**.
  - Other tiers scaled accordingly in Sonarr/Radarr profiles.
- **Consequences:**
  - Avoids bloat while allowing slightly larger YTS/freeleech within Max.
  - Size heuristic aligns with preferences.

## ADR-019: Requests app — Jellyseerr over Overseerr

- **Status:** Approved
- **Context:**
  Jellyfin-first household; want simple authentication and UX for family.
- **Decision:**
  - Use Jellyseerr; connect to Jellyfin, Sonarr, and Radarr.
  - Household users authenticate via Jellyfin accounts.
- **Consequences:**
  - Seamless request flow; optional auto-approve for household members.

## ADR-020: Healthchecks — simple HTTP endpoints per service

- **Status:** Approved
- **Context:**
  Compose needs reliable health signals that don’t flap.
- **Decision:**
  - Plex `/identity`; Jellyseerr HTTP `/`; Sonarr/Radarr `/ping`; Bazarr `/`; qBittorrent `/api/v2/app/version`; Prowlarr `/`; FlareSolverr `/health`; Gluetun built-in.
- **Consequences:**
  - `docker ps` surfaces unhealthy services quickly.
  - Faster, clearer troubleshooting.

## ADR-021: Container hygiene — defer pinning; consistent users/groups

- **Status:** Approved
- **Context:**
  Rapid iteration during Phase 7 with predictable file ownership.
- **Decision:**
  - Keep images on `:latest` during setup; pin digests later.
  - Map `PUID=1000` and `PGID=1000`; add `video` and `render` groups for Jellyfin/Plex.
  - Keep configs under `/srv/config/<service>`.
- **Consequences:**
  - Fast changes now; reproducibility when digests are pinned.
  - Consistent permissions across containers.

