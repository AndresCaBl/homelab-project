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
