# Decisions & Rationale (ADR-style summaries)

## ADR-000: Hostnames & IP Plan
- **Status:** Proposed
- **Context:** Two Lenovo X1 Yoga Gen 5 laptops used as nodes.
- **Decision:** Use `srv-media` (Ubuntu) and `lab-proxmox` (Proxmox) with reserved IPs in 192.168.4.0/24.
- **Consequences:** Consistent addressing, easy migration.

## ADR-001: Everything under /srv on hosts
- **Status:** Proposed
- **Decision:** Use `/srv/{media,downloads,config,compose,bin,backup}` with UUID-based mounts for USB drives.

## ADR-002: Everything-as-Code via Docker Compose
- **Status:** Proposed
- **Decision:** Each stack has its own compose project and `.env.example` committed (no secrets).
