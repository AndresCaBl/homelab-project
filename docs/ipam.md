# IP Address Management (IPAM)

**Domain:** `home.arpa`

**Subnets:**
- **Infra (VLAN 1)** → `10.10.1.0/24` (GW `10.10.1.1`)
- **Servers (VLAN 2)** → `10.10.2.0/24` (GW `10.10.2.1`)
- **Clients (VLAN 3)** → `10.10.3.0/24` (GW `10.10.3.1`)
- **IoT (VLAN 4)** → `10.10.4.0/24` (GW `10.10.4.1`) — not in use
- **Guest (VLAN 10)** → `10.10.10.0/24` (GW `10.10.10.1`) — not in use

---

## Infra (VLAN 1 — 10.10.1.0/24)

**DHCP:** pool: `10.10.1.50–199`
**DNS:** Pi-hole on `srv-network` advertised as DNS for all VLANs

| IP            | Hostname                  | MAC Address | Device / Role                                | Notes |
|---------------|---------------------------|-------------|----------------------------------------------|-------|
| **10.10.1.1** | **gw-uxg.home.arpa**      |             | **UniFi UXG-Lite** (gateway)  | Controller override → `srv-network.home.arpa` |
| **10.10.1.2** | **dns-pihole.home.arpa**  |             | **Pi-hole** (Docker on `srv-network`)        | Primary DNS |
| **10.10.1.3** | **sw-flex-5p.home.arpa**  |             | **UniFi USW Flex Mini** (management)         | Static/reservation |
| **10.10.1.10**| **srv-network.home.arpa** |             | **Infra host** (Docker: UniFi + Pi-hole)     | Static/reservation |

Reserved (optional):
- `10.10.1.30–39` future switches/APs
- `10.10.1.40–49` infra VIPs/services (unbound/syslog/etc.)

---

## Servers (VLAN 2 — 10.10.2.0/24)

**DHCP:** Off (use static/reservations)

| IP            | Hostname               | MAC Address | Device / Role                               | Notes |
|---------------|------------------------|-------------|---------------------------------------------|-------|
| **10.10.2.2** | **srv-media.home.arpa**|             | Media + automation host                     | Ubuntu 24.04.3 LTS |

Reserved (optional):
- `10.10.2.10–19` future servers/VMs

Removed:
- `lab-proxmox` (decommissioned)

---

## Clients (VLAN 3 — 10.10.3.0/24)

**DHCP:** On (`10.10.3.50–199`)
**Notes:** Eero in bridge mode on Clients VLAN

| IP          | Hostname              | MAC Address | Device / Role      | Notes |
|-------------|-----------------------|-------------|--------------------|------|
| 10.10.3.2   | ap-eero.home.arpa      |            | Eero (bridge mode) |      |

---

## IoT (VLAN 4 — 10.10.4.0/24)

Not in use. Intended isolation: block IoT → Servers by default.

---

## Guest (VLAN 10 — 10.10.10.0/24)

Not in use. Intended isolation: guest traffic is internet-only.
Current WAP's do not support wireless VLAN's

---

## DHCP + DNS

**DHCP DNS per scope:**
- Primary: `10.10.1.2` (`dns-pihole.home.arpa`)
- Secondary: `none` (`secondary pi-hole to be deployed for redundancy`)

**Pi-hole Local DNS records (A):**
- `gw-uxg.home.arpa` → `10.10.1.1`
- `dns-pihole.home.arpa` → `10.10.1.2`
- `sw-flex-5p.home.arpa` → `10.10.1.3`
- `srv-network.home.arpa` → `10.10.1.10`
- `srv-media.home.arpa` → `10.10.2.2`

---

## Change log

| Date (AEST) | Change |
|-------------|--------|
| 2025-09-12  | Initial IPAM and DNS plan |
| 2026-02-17  | Updated domain to `home.arpa`, removed `lab-proxmox`, corrected `srv-media` to `10.10.2.2`, clarified Pi-hole/UniFi on `srv-network` |
