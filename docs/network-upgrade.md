# Network Cutover Runbook (Home Lab) — v2.0 (UniFi)

**Project:** Homelab — Network migration to **UniFi UXG-Lite** + **Pi-hole** + VLANs
**Change type:** Planned maintenance (short outage window)

---

## Scope & Goals
- Replace **eero-as-router** with **UniFi UXG-Lite** (gateway/firewall) and introduce **VLAN** segmentation.
- Self-host **UniFi Network Application** on **srv-network** (Tiny PC).
- Use **Pi-hole** for DNS/ad-blocking; DHCP from the **UXG-Lite**.
- Keep media/automation stack working (Jellyfin, Plex, Sonarr/Radarr/Bazarr/Prowlarr/qBit via Gluetun).
- Migrate **IP literals → hostnames**; keep **Tailscale** for out-of-band access.

---

## FQDNs, Key IPs & Terminology

**FQDNs:**
- `gw-uxg.home` (UXG-Lite), `dns-pihole.home` (Pi-hole), `sw-flex-5p.home` (USW Flex Mini)
- `srv-network.home` (controller/infra Tiny), `srv-media.home`, `lab-proxmox.home`

**Key IPs (static/reserved):**
- **10.10.1.1** `gw-uxg.home` — UXG-Lite LAN
- **10.10.1.2** `dns-pihole.home` — Pi-hole (on srv-network; prefer macvlan)
- **10.10.1.3** `sw-flex-5p.home` — USW Flex Mini mgmt
- **10.10.1.10** `srv-network.home` — Lenovo Tiny (UniFi controller + logging/monitoring)
- **10.10.2.1** `srv-media.home` — Media/automation host
- **10.10.2.2** `lab-proxmox.home` — Proxmox host

**Terminology:** **GW** = default gateway IP for a VLAN/subnet. Example: Infra GW is `10.10.1.1`.

---

## VLAN & Subnet Plan
| VLAN | Purpose   | Subnet          | Gateway IP     | DHCP | Notes |
|---:|---|---|---|:---:|---|
| 1 | **Infra**   | `10.10.1.0/24`  | `10.10.1.1`    | Off  | Controller, Pi-hole, switch mgmt |
| 2 | **Servers** | `10.10.2.0/24`  | `10.10.2.1`*   | Off  | Static/reserved (srv-media, lab-proxmox) |
| 3 | **Clients** | `10.10.3.0/24`  | `10.10.3.1`    | On   | Primary client scope |
| 4 | **IoT**     | `10.10.4.0/24`  | `10.10.4.1`    | Later| For TVs/devices; isolate from Servers |
| 10| **Guest**   | `10.10.10.0/24` | `10.10.10.1`   | Later| Requires AP with SSID→VLAN |

\* Gateway IP for Servers is owned by UXG-Lite’s VLAN 2 interface; hosts use static/reservations.

**DHCP pools (initial):**
- Clients: `10.10.3.50–199` (DNS = `10.10.1.2`, Alt DNS = `10.10.1.1`)
- Infra/Servers: DHCP **Off** (use static/reservations)

---

## USW Flex Mini Port/VLAN Map (`sw-flex-5p.home`)

**VLANs:** 1=Infra, 2=Servers, 3=Clients, 4=IoT, 10=Guest

| Port | Mode  | Untagged VLAN | Tagged VLANs | PVID | Cable to |
|---:|---|---|---|---:|---|
| 1 | Trunk | 1 | 2,3,4,10 | 1 | **UXG-Lite LAN** (802.1Q trunk) |
| 2 | Access| 2 | — | 2 | **Unmanaged 5-port** (Servers → srv-media, lab-proxmox) |
| 3 | Access| 1 | — | 1 | **srv-network** (Tiny; Infra) |
| 4 | Access| 3 | — | 3 | **eero** (Bridge Mode) |
| 5 | Access| 3 | — | 3 | Admin laptop / client |

Switch features: **Enable IGMP Snooping** and **Loop Prevention**.
Mgmt IP (VLAN 1): **`10.10.1.3/24`**, GW `10.10.1.1`.

---

## Phase 1 — Prep & Freeze
- Freeze changes to media/automation apps until after cutover.
- Ensure **Tailscale** is running on `srv-media` and `lab-proxmox`.
- Confirm final hostnames/IPs (above). Prepare to replace **IP literals → hostnames** in configs (Plex `ADVERTISE_IP`, Jellyseerr, Prowlarr Apps, Homepage tiles).
- Gather ISP auth (DHCP/PPPoE), UniFi admin credentials.
- Back up key data: `/srv/config` on servers; export existing settings where applicable.

---

## Phase 2 — Controller & Pi-hole host (srv-network) ready
- **srv-network (Tiny)**: Ubuntu Server LTS installed; Docker/Compose verified (your preflight passed).
- Timezone set to **Australia/Brisbane**.
- Decide Pi-hole **networking**:
  - **Preferred:** **macvlan** on Infra (Pi-hole gets **10.10.1.2**)
  - Alternative: host-network (requires freeing port 53 on host)
- Stage but **don’t** rely on these yet: UniFi controller (on srv-network), Pi-hole.

---

## Phase 3 — Adoption Bubble (offline, safe)
**Goal:** Adopt UXG-Lite and Flex Mini to the local controller before touching production.

**Wiring (no WAN):**
- **UXG-Lite LAN → Flex Mini Port 1** (trunk)
- **srv-network → Flex Mini Port 3** (Infra)
- **Admin laptop → Flex Mini Port 5** (Clients for now)

**In UniFi controller (srv-network):**
- Complete first-run, create site.
- **Adopt** UXG-Lite and Flex Mini.
- Create networks: Infra (VLAN 1), Servers (2), Clients (3), IoT (4), Guest (10) with subnets above.
- Set **Controller Host/IP override** to `srv-network.home` (or `10.10.1.10`).

**Configure DHCP (bubble stage):**
- Leave **DHCP Off** except **Clients VLAN (3)** can be enabled for bubble tests if desired.
- Under DHCP options for Clients: DNS1=`10.10.1.2` (Pi-hole), DNS2=`10.10.1.1` (UXG).

**Reservations (create now):**
- `srv-network.home` → **10.10.1.10**
- `dns-pihole.home` → **10.10.1.2** (if macvlan)
- `sw-flex-5p.home` → **10.10.1.3**
- `srv-media.home` → **10.10.2.1**
- `lab-proxmox.home` → **10.10.2.2**
- (Optional) `ap-eero.home` → **10.10.3.2**

**Program ports (Flex Mini):** per table above.

---

## Phase 4 — Cutover (short window)
**Recabling:**
- **NTD/Modem → UXG-Lite WAN**
- **UXG-Lite LAN (trunk) → Flex Mini Port 1**
- **Unmanaged 5-port (Servers) → Flex Mini Port 2**
- **srv-network (Tiny) → Flex Mini Port 3 (Infra)**
- **eero (Bridge Mode) → Flex Mini Port 4**
- **Admin laptop → Flex Mini Port 5**

**Bring-up in UniFi:**
- Enable **DHCP on Clients (VLAN 3)** — pool `10.10.3.50–199`.
- Confirm **reservations** above.
- **DNS per scope:** Clients use Pi-hole (`10.10.1.2`) primary, UXG (`10.10.1.1`) secondary.

**Pi-hole:**
- Upstream resolvers set; **Conditional Forwarding** to `10.10.1.1`, domain `home`.
- Add **Local DNS records**:
  `gw-uxg.home → 10.10.1.1`, `dns-pihole.home → 10.10.1.2`,
  `sw-flex-5p.home → 10.10.1.3`, `srv-network.home → 10.10.1.10`,
  `srv-media.home → 10.10.2.1`, `lab-proxmox.home → 10.10.2.2`,
  (optional) `ap-eero.home → 10.10.3.2`.

**Readdress servers (one at a time):**
- Move `srv-media`/`lab-proxmox` behind Port 2 path (Servers VLAN). Verify hostnames resolve to new IPs and SSH works by FQDN.

---

## Phase 5 — Validation & Stabilisation
**Clients (VLAN 3):**
- Receives **10.10.3.x**, **GW 10.10.3.1**, **DNS 10.10.1.2**; Internet OK.
- Pi-hole shows per-client queries (not just the gateway).

**Controller & Infra:**
- UXG-Lite and Flex Mini **Connected** in UniFi; Controller override correct.

**Apps & Services:**
- Jellyfin health OK (`/health` 200).
- Plex loads at `http://srv-media.home:32400/web`. If discovery banner missing, **add server manually**; set `ADVERTISE_IP` to `http://srv-media.home:32400/`.
- Sonarr/Radarr ↔ qBit (via `gluetun:8080`) OK; Prowlarr/FlareSolverr OK; Bazarr OK.

**Firewall posture:**
- Keep **permissive inter-VLAN** rules during stabilisation (24–48h). Tighten later.

---

## Phase 6 — Clean-up & Docs
- Replace remaining **IP literals → hostnames** in compose/configs/scripts/dashboards.
- Document final static reservations, DHCP pools, and **port/VLAN map** in repo.
- Export UniFi backup; set controller and UXG timezone **Australia/Brisbane**.
- Verify **no WAN port-forwards** on UXG.
- Plan next steps: IoT VLAN rules, Guest VLAN (when SSID→VLAN ready), Unbound tuning, Prometheus/Grafana/Loki baseline dashboards & retention, image pinning & healthchecks.

---

## Rollback Plan (quick)
**Goal:** return to eero-routed `192.168.4.0/22` quickly if needed.

1) In UniFi, **disable DHCP** on new VLANs.
2) **Power down UXG-Lite** (or leave in place but unused).
3) **NTD → eero WAN**, set **eero to Router Mode**.
4) Option A: uplink Flex Mini Port 1 to eero LAN as a plain access edge; or Option B: reconnect devices directly to eero.
5) Confirm clients get `192.168.4.x` leases; DNS reverts to previous.
6) Because you used **hostnames**, most app configs remain valid; only DNS server choice might need a temporary revert.

---

## Service Discovery Across VLANs — Practical Notes
- **Don’t expect mDNS (5353), SSDP (1900), or Plex GDM (32410–32414) to traverse VLANs.**
- **Works now:** direct connections by **hostname**; Plex with `ADVERTISE_IP`.
- **If you later need cross-VLAN discovery:**
  - Use UniFi’s **Bonjour Gateway** (mDNS proxy) for specific services between **Clients↔IoT**; or
  - Run **Avahi (reflector)** and/or **udpbroadcastrelay** on a dual-homed helper (restricted to needed VLAN pairs/ports).

---
