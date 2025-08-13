# Decisions & Rationale (ADR-style summaries)

## ADR-000: Hostnames & IP Plan
- **Status:** APROVED
- **Context:** Two Lenovo X1 Yoga Gen 5 laptops used as nodes.
- **Decision:** Use `srv-media` (Ubuntu) and `lab-proxmox` (Proxmox) with reserved IPs in 192.168.4.0/24.
- **Consequences:** Consistent addressing, easy migration.

## ADR-001: Everything under /srv on hosts
- **Status:** Proposed
- **Decision:** Use `/srv/{media,downloads,config,compose,bin,backup}` with UUID-based mounts for USB drives.

## ADR-002: Everything-as-Code via Docker Compose
- **Status:** Proposed
- **Decision:** Each stack has its own compose project and `.env.example` committed (no secrets).

## ADR-003: Repo workflow
- **Decision:** Use WSL for git and scripting to match Linux hosts.
- **Consequences:** Avoid CR/LF issues and Windows path quirks.

## ADR-004: Timezone & IDs
- **Decision:** Use TZ=Australia/Brisbane, PUID/PGID=1000 for containers.
- **Consequences:** Consistent file ownership across hosts.

## ADR-005: IP convention
- **Decision:** Reserve .90 (srv-media), .91 (lab-proxmox), .92 (Pi-hole LXC).
- **Consequences:** Predictable addressing and future VLAN carve‑outs.

## ADR-006: Disable Wi‑Fi for lab hosts
- **Context**: Consistent addressing and simpler routing
- **Decision**: Use Ethernet only (adapters + unmanaged switch)
- **Status**: Accepted (2025-08-13)
- **Consequences**: Fewer moving parts, more stable lab

## ADR-007: IPv4-only for Phase 1
- **Context**: Reduce complexity; align with early CCNA study
- **Decision**: Disable IPv6 on Eero and hosts
- **Status**: Accepted (2025-08-13)
- **Consequences**: Simpler firewalling, consistent tests; revisit in later phase

## ADR-008
: DHCP reservations on Eero
- **Context**: Predictable addressing for `srv-media` & `lab-proxmox`
- **Decision**: Reserve 192.168.4.90 and .91 to Ethernet MACs
- **Status**: Accepted (2025-08-13)