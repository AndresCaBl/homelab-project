# IP Address Management (IPAM)

**Domain:** `.home`
**VLANs/Subnets:**
- **Infra (VLAN 1)** → `10.10.1.0/24`
- **Servers (VLAN 2)** → `10.10.2.0/24`
- **Clients (VLAN 3)** → `10.10.3.0/24`
- **IoT (VLAN 4)** → `10.10.4.0/24`
- **Guest (VLAN 10)** → `10.10.10.0/24`

---

## Infra (VLAN 1 — 10.10.1.0/24)

**DHCP:** Off (optional break-glass pool: `10.10.1.200–219`)
**Notes:** Controller = `srv-network.home`. Pi-hole advertised via DHCP as primary DNS for all VLANs.

| IP         | Hostname            | MAC Address        | Device / Role                                   | Notes |
|------------|---------------------|--------------------|--------------------------------------------------|-------|
| **10.10.1.1**  | **gw-uxg.home**       |                    | **UXG-Lite** (Gateway LAN IP)                   | Controller override → `srv-network.home` |
| **10.10.1.2**  | **dns-pihole.home**   |                    | **Pi-hole** (DNS; on srv-network, ideally macvlan) | Primary DNS for all scopes |
| **10.10.1.3**  | **sw-flex-5p.home**   |                    | **USW Flex Mini** (management)                  | Set in UniFi → Devices |
| **10.10.1.10** | **srv-network.home**  |                    | **Lenovo Tiny** (infra node: UniFi, monitoring, logging) | Static/reservation |
| 10.10.1.30–39 | (future-switch/ap)    |                    | Future UniFi switches/APs                        | Reserve block |
| 10.10.1.40–49 | (infra-services)      |                    | Future infra VIPs (e.g., Unbound, syslog)        | Optional |

---

## Servers (VLAN 2 — 10.10.2.0/24)

**DHCP:** Off (use static or reservations)
**Notes:** Unmanaged 5-port connects to Flex Mini Port 2 (ACCESS=VLAN 2).

| IP         | Hostname             | MAC Address        | Device / Role                              | Notes |
|------------|----------------------|--------------------|--------------------------------------------|-------|
| **10.10.2.1** | **srv-media.home**     |                    | Media + automation (Jellyfin, Plex, Sonarr/Radarr/Bazarr, qBit) |  |
| **10.10.2.2** | **lab-proxmox.home**   |                    | Proxmox host                               | VMs/LXCs as needed |
| 10.10.2.10–19 | (future-servers)       |                    | Future servers/VMs                          | Reserve block |

---

## Clients (VLAN 3 — 10.10.3.0/24)

**DHCP:** On (`10.10.3.50–199`)
**Notes:** Eero in Bridge Mode on Clients.

| IP          | Hostname          | MAC Address | Device / Role               | Notes |
|-------------|-------------------|-------------|-----------------------------|-------|
| 10.10.3.2   | ap-eero.home      |             | Eero (Bridge Mode)          | Reserve for convenience |
| (dynamic)   | —                 | —           | Laptops/phones/PCs          | Leases from pool |

---

## IoT (VLAN 4 — 10.10.4.0/24) — Later

**DHCP:** On (`10.10.4.50–199`)
**Notes:** Keep **IoT → Servers** blocked by default.

| IP          | Hostname          | MAC Address | Device / Role           | Notes |
|-------------|-------------------|-------------|-------------------------|-------|
| (reserve)   | iot-hub.home      |             | IoT hub/bridge          |       |
| (dynamic)   | —                 | —           | IoT devices             | Use DHCP reservations if needed |

---

## Guest (VLAN 10 — 10.10.10.0/24) — Later

**DHCP:** On (`10.10.10.50–199`)
**Notes:** Guest isolated; no statics planned.

| IP          | Hostname          | MAC Address | Device / Role | Notes |
|-------------|-------------------|-------------|---------------|-------|
| (dynamic)   | —                 | —           | Guest devices | Isolated network |

---

## DHCP & DNS Settings (UniFi / Pi-hole)

- **DHCP DNS per scope:**
  - **Primary:** `10.10.1.2` (`dns-pihole.home`)
  - **Secondary:** `10.10.1.1` (`gw-uxg.home`)

- **Local DNS (Pi-hole → Local DNS → DNS Records):**
  Add A-records for each static host:
  - `gw-uxg.home → 10.10.1.1`
  - `dns-pihole.home → 10.10.1.2`
  - `sw-flex-5p.home → 10.10.1.3`
  - `srv-network.home → 10.10.1.10`
  - `srv-media.home → 10.10.2.1`
  - `lab-proxmox.home → 10.10.2.2`
  - `ap-eero.home → 10.10.3.2` (optional)

---

## Adoption & Reservations (UniFi quick steps)

1. **Adopt devices** (UXG-Lite, Flex Mini) in the controller on `srv-network.home`.
2. Set **Controller Host/IP override** to `srv-network.home` (or `10.10.1.10`).
3. Create **DHCP Reservations** with MACs for:
   - `gw-uxg.home` → `10.10.1.1`
   - `sw-flex-5p.home` → `10.10.1.3`
   - `srv-network.home` → `10.10.1.10`
   - `srv-media.home` → `10.10.2.1`
   - `lab-proxmox.home` → `10.10.2.2`
   - `ap-eero.home` → `10.10.3.2` (optional)


> - gw-uxg.home: `__MAC__`
> - sw-flex-5p.home: `__MAC__`
> - srv-network.home: `__MAC__`
> - srv-media.home: `__MAC__`
> - lab-proxmox.home: `__MAC__`
> - ap-eero.home (opt): `__MAC__`

---

## Notes / Decisions

- **Pi-hole placement:** prefer macvlan @ `10.10.1.2` (clean :53 ownership).
- **Plex/Jellyfin discovery:** rely on hostnames / Plex `ADVERTISE_IP`. Add Bonjour Gateway later only if needed.
- **Firewalling:** Initially permissive between Infra/Servers/Clients; tighten later (block IoT → Servers, keep Guest isolated).

---

## Change Log

| Date (AEST) | Change | By |
|-------------|--------|----|
| 2025-09-12  | Initial IPAM with Infra/Servers/Clients, reservations, and DNS plan | andres/ai |
