```md
# Architecture Decision Record (ADR) Log — Homelab

Append-only log of architecturally significant decisions.
Current addressing and naming: `docs/ipam.md`.

---

## Index

| ADR | Title | Status | Date (AEST) | Confidence |
|---|---|---|---|---|
| ADR-0001 | Internal DNS domain (`home.arpa`) | Accepted | 2026-02-17 | High |
| ADR-0002 | Phase 1 network: eero router + flat LAN (`192.168.4.0/22`) | Superseded | 2025-09-12 | High |
| ADR-0003 | Phase 2 network: UniFi UXG-Lite + VLAN segmentation | Accepted | 2026-02-17 | High |
| ADR-0004 | DHCP strategy (current: Clients only) | Accepted | 2026-02-17 | High |
| ADR-0005 | DNS strategy: Pi-hole on `srv-network` | Accepted | 2026-02-17 | Medium |
| ADR-0006 | Host inventory and roles | Accepted | 2026-02-17 | High |
| ADR-0007 | `/srv` as the root for persistent data | Accepted | 2025-09-12 | High |
| ADR-0008 | Everything-as-code with Docker Compose | Accepted | 2025-09-12 | High |
| ADR-0009 | Repo workflow: WSL for git + scripting | Accepted | 2025-09-12 | High |
| ADR-0010 | Timezone and container user IDs | Accepted | 2025-09-12 | High |
| ADR-0011 | Ethernet-first for servers | Accepted | 2025-09-12 | High |
| ADR-0012 | IPv4-only during early build | Accepted | 2025-09-12 | Medium |
| ADR-0013 | SSH key-based auth as default | Accepted | 2025-09-12 | High |
| ADR-0014 | Remote access via Tailscale | Accepted | 2025-09-12 | High |
| ADR-0015 | Storage layout: USB libraries + SSD cache | Accepted | 2025-09-12 | High |
| ADR-0016 | Media frontends: Plex primary; Jellyfin secondary | Accepted | 2025-09-12 | High |
| ADR-0017 | Subtitle handling: import existing; Bazarr fills gaps | Accepted | 2025-09-12 | Medium |
| ADR-0018 | Seeding strategy: SSD-first, copy-on-import (no hardlinks) | Accepted | 2025-09-12 | High |
| ADR-0019 | Release selection preferences (custom formats + indexer priorities) | Accepted | 2025-09-12 | Medium |
| ADR-0020 | Quality size caps (MB/min) | Accepted | 2025-09-12 | Medium |
| ADR-0021 | Requests app: Jellyseerr | Accepted | 2025-09-12 | High |
| ADR-0022 | Health checks: simple per-service endpoints | Accepted | 2025-09-12 | Medium |
| ADR-0023 | Container hygiene: iterate on `:latest`, pin later | Accepted | 2025-09-12 | Medium |
| ADR-0024 | `srv-media` networking: NetworkManager renderer | Accepted | 2025-09-12 | High |
| ADR-0025 | Wireless VLANs deferred (current AP limitation) | Accepted | 2026-02-17 | High |

---

## ADR-0001: Internal DNS domain (`home.arpa`)
- **Status:** Accepted
- **Date:** 2026-02-17
- **Confidence:** High
- **Context:** Internal hostnames needed a stable namespace that won’t collide with public DNS.
- **Options considered:** `.home`, `.local`, `home.arpa`
- **Decision:** Use `home.arpa` for internal DNS.
- **Consequences:** Local DNS and documentation use `*.home.arpa`.

---

## ADR-0002: Phase 1 network: eero router + flat LAN (`192.168.4.0/22`)
- **Status:** Superseded (replaced by ADR-0003)
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Early lab setup prioritized speed and minimal moving parts.
- **Options considered:** flat LAN behind eero; VLAN segmentation from day one
- **Decision:** Use a flat LAN behind eero with DHCP reservations for hosts.
- **Consequences:** Early configs used IP literals and were refactored during cutover.

---

## ADR-0003: Phase 2 network: UniFi UXG-Lite + VLAN segmentation
- **Status:** Accepted
- **Date:** 2026-02-17
- **Confidence:** High
- **Context:** The lab needed segmentation, predictable addressing, and centralized network management.
- **Options considered:** keep eero routing; UniFi gateway + managed switching
- **Decision:** Use UniFi UXG-Lite as gateway/firewall with VLANs defined in `docs/ipam.md`.
- **Consequences:** Network state is documented by runbooks and IPAM, not ad-hoc device configs.

---

## ADR-0004: DHCP strategy (current: Clients only)
- **Status:** Accepted
- **Date:** 2026-02-17
- **Confidence:** High
- **Context:** Infrastructure nodes needed stable addresses; client devices did not.
- **Options considered:** DHCP on all VLANs; DHCP on Clients only with static/reservations for Infra/Servers
- **Decision:** DHCP enabled for Clients VLAN only. Infra and Servers use static/reservations.
- **Consequences:** Server addressing is stable; client churn stays isolated to the Clients VLAN.

---

## ADR-0005: DNS strategy: Pi-hole on `srv-network`
- **Status:** Accepted
- **Date:** 2026-02-17
- **Confidence:** Medium
- **Context:** The lab needed a single DNS resolver with local records for `home.arpa`.
- **Options considered:** gateway DNS only; Pi-hole as primary DNS
- **Decision:** Run Pi-hole on `srv-network` and advertise it as DNS for VLANs.
- **Consequences:** DNS depends on `srv-network`; redundancy requires a second resolver.
- **Needs confirmation:** Pi-hole IP ownership for `10.10.1.2` (macvlan vs bridge/port mapping). Record the chosen mode when verified.

---

## ADR-0006: Host inventory and roles
- **Status:** Accepted
- **Date:** 2026-02-17
- **Confidence:** High
- **Context:** Reduce operational overhead and clarify service ownership.
- **Options considered:** dedicated hypervisor node; consolidated infra host + dedicated media host
- **Decision:**
  - `srv-network`: UniFi Network Application + Pi-hole (Docker)
  - `srv-media`: media + automation stacks
  - `lab-proxmox`: removed
- **Consequences:** Infra and media responsibilities are explicit and documented by hostname.

---

## ADR-0007: `/srv` as the root for persistent data
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Persistent data needed stable paths to support rebuilds and migrations.
- **Options considered:** distro defaults; standardize under `/srv`
- **Decision:** Store persistent data under `/srv`.
- **Consequences:** Path conventions are consistent across services and hosts.

---

## ADR-0008: Everything-as-code with Docker Compose
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Service deployments needed to be repeatable and reviewable.
- **Options considered:** manual installs; Compose-managed containers
- **Decision:** Run services as Compose projects; commit `.env.example`; keep secrets out of git.
- **Consequences:** Changes are tracked and can be rolled back.

---

## ADR-0009: Repo workflow: WSL for git + scripting
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Windows tooling introduced CR/LF and path issues.
- **Options considered:** native Windows workflow; WSL-first workflow
- **Decision:** Use WSL for git operations and scripting.
- **Consequences:** Fewer line-ending and permission mismatches.

---

## ADR-0010: Timezone and container user IDs
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Logs and file ownership needed to align across hosts and containers.
- **Options considered:** defaults; standard TZ/PUID/PGID
- **Decision:** Use `TZ=Australia/Brisbane`, `PUID=1000`, `PGID=1000` where supported.
- **Consequences:** Predictable timestamps and consistent ownership under `/srv`.

---

## ADR-0011: Ethernet-first for servers
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Stable addressing and fewer wireless variables were required for servers.
- **Options considered:** Wi-Fi; Ethernet
- **Decision:** Prefer Ethernet for server/infra nodes.
- **Consequences:** More predictable connectivity and troubleshooting.

---

## ADR-0012: IPv4-only during early build
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** Medium
- **Context:** Reduce moving parts during buildout.
- **Options considered:** dual-stack; IPv4-only
- **Decision:** Operate IPv4-only initially; revisit IPv6 later.
- **Consequences:** Simpler routing and firewalling while iterating.

---

## ADR-0013: SSH key-based auth as default
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Admin access needed to be secure and consistent across hosts.
- **Options considered:** password auth; key-based auth with password auth disabled
- **Decision:** Use a dedicated Ed25519 keypair and disable SSH password authentication after validation.
- **Consequences:** Consistent login flow and reduced credential exposure.

---

## ADR-0014: Remote access via Tailscale
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Remote access was required without WAN port forwarding.
- **Options considered:** port forwards; site-to-site VPN; Tailscale
- **Decision:** Use Tailscale with MagicDNS enabled.
- **Consequences:** Remote admin remains available across LAN changes.

---

## ADR-0015: Storage layout: USB libraries + SSD cache
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Downloads/seeding needed SSD I/O; libraries needed capacity.
- **Options considered:** all-on-USB; SSD cache + USB library
- **Decision:**
  - USB library mounts: `/srv/media/movies`, `/srv/media/tv` (UUID mounts, `noatime`)
  - SSD cache: `/srv/cache/downloads/{incomplete,seeding,watch}`
  - Config: `/srv/config/<service>`
  - Compose: `/srv/compose/<stack>`
  - Backup: `/srv/backup/{configs,db_dumps}`
- **Consequences:** Churn stays on SSD; library paths remain stable.

---

## ADR-0016: Media frontends: Plex primary; Jellyfin secondary
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Household playback needed broad client support without locking into a single frontend.
- **Options considered:** Plex only; Jellyfin only; run both
- **Decision:** Plex is the primary frontend. Jellyfin is deployed and kept available but is not the default.
- **Consequences:** Operational checks prioritize Plex; Jellyfin remains available for testing/backup or specific clients.

---

## ADR-0017: Subtitle handling: import existing; Bazarr fills gaps
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** Medium
- **Context:** Many files already had valid subtitles; duplicates caused clutter.
- **Options considered:** always fetch; import existing + fetch missing only
- **Decision:** Import existing subtitles via Sonarr/Radarr; Bazarr fetches missing/additional only.
- **Consequences:** Fewer duplicates and less subtitle churn.

---

## ADR-0018: Seeding strategy: SSD-first, copy-on-import (no hardlinks)
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Seeding performance mattered; USB writes during seeding were undesirable.
- **Options considered:** hardlinks into library; copy-on-import with SSD seeding
- **Decision:** Copy on import; hardlinks off; keep torrents seeding from SSD paths.
- **Consequences:** Stable library paths on USB; sustained seeding performance.

---

## ADR-0019: Release selection preferences (custom formats + indexer priorities)
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** Medium
- **Context:** Automated selection needed bias toward preferred sources when quality is equivalent.
- **Options considered:** default ordering only; custom formats + indexer priorities
- **Decision:** Use custom formats and indexer priorities to bias selection.
- **Consequences:** More predictable automation; requires periodic tuning.

---

## ADR-0020: Quality size caps (MB/min)
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** Medium
- **Context:** Avoid oversized encodes while still accepting good WEB releases.
- **Options considered:** no caps; MB/min caps per tier
- **Decision:**
  - Movies (1080p WEB): preferred ~20–22 MB/min; max ~35–36 MB/min
  - TV (1080p WEB): preferred ~16 MB/min; max ~26 MB/min
- **Consequences:** Storage stays lean; edge-case releases may be rejected.

---

## ADR-0021: Requests app: Jellyseerr
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Household requests needed a simple workflow tied to existing auth.
- **Options considered:** Overseerr; Jellyseerr
- **Decision:** Use Jellyseerr integrated with Jellyfin, Sonarr, and Radarr.
- **Consequences:** Requests use Jellyfin accounts; the request flow remains separate from Plex.

---

## ADR-0022: Health checks: simple per-service endpoints
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** Medium
- **Context:** Troubleshooting needed fast, low-noise signals.
- **Options considered:** none; lightweight HTTP-based checks
- **Decision:** Use simple per-service endpoints (where available).
- **Consequences:** Faster triage when containers are unhealthy.

---

## ADR-0023: Container hygiene: iterate on `:latest`, pin later
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** Medium
- **Context:** Early setup required frequent changes.
- **Options considered:** pin immediately; iterate on `:latest` then pin
- **Decision:** Use `:latest` during active buildout; pin versions/digests once stable.
- **Consequences:** Faster iteration; some risk from upstream changes until pinning is complete.

---

## ADR-0024: `srv-media` networking: NetworkManager renderer
- **Status:** Accepted
- **Date:** 2025-09-12
- **Confidence:** High
- **Context:** Cockpit networking and update status required NetworkManager integration.
- **Options considered:** systemd-networkd; NetworkManager
- **Decision:** Use `renderer: NetworkManager` for the primary interface; keep Docker/Tailscale unmanaged by NM.
- **Consequences:** Cockpit networking and update status behave consistently.

---

## ADR-0025: Wireless VLANs deferred (current AP limitation)
- **Status:** Accepted
- **Date:** 2026-02-17
- **Confidence:** High
- **Context:** Guest/IoT VLANs require SSID-to-VLAN mapping; current APs do not support wireless VLANs.
- **Options considered:** enable partial isolation now; define VLANs and defer wireless segmentation
- **Decision:** Keep Guest and IoT VLANs defined but unused until AP upgrade.
- **Consequences:** Wi-Fi remains on Clients VLAN; guest/IoT wireless segmentation is a planned upgrade.
```
