# Network Cutover Runbook — UniFi (UXG-Lite + VLANs + Pi-hole)

**Reference:** `docs/ipam.md` (authoritative naming + addressing)

## Change summary

- Gateway/firewall moved from eero to UniFi UXG-Lite.
- UniFi Network Application and Pi-hole run on `srv-network` (Docker).
- DHCP served by UXG-Lite (Clients VLAN enabled; Infra/Servers static).
- DNS served by Pi-hole (`dns-pihole.home.arpa`).
- Hostnames standardised on `home.arpa`.

## Current state (post-cutover)

- `srv-network.home.arpa`: UniFi Network Application + Pi-hole (Docker)
- `srv-media.home.arpa`: `10.10.2.2` (Ubuntu 24.04.3 LTS)
- `lab-proxmox`: removed

## VLANs

| VLAN | Purpose  | Subnet          | Gateway       | DHCP |
| 1  | Infra    | `10.10.1.0/24`   | `10.10.1.1`  | On  |
| 2  | Servers  | `10.10.2.0/24`   | `10.10.2.1`  | Off |
| 3  | Clients  | `10.10.3.0/24`   | `10.10.3.1`  | On  |
| 4  | IoT      | `10.10.4.0/24`   | `10.10.4.1`  | Not in use |
| 10 | Guest    | `10.10.10.0/24`  | `10.10.10.1` | Not in use |

Clients VLAN DNS: `10.10.1.2` (Pi-hole)

## Switch port map — USW Flex Mini (`sw-flex-5p.home.arpa`)

| Port | Mode   | Untagged VLAN | Tagged VLANs | Cable to |
| 1  | Trunk  | 1              | 2,3,4,10     | UXG-Lite LAN |
| 2  | Access | 2              | —            | Unmanaged 5-port (Servers → `srv-media`) |
| 3  | Access | 1              | —            | `srv-network` |
| 4  | Access | 3              | —            | eero (Bridge Mode) |
| 5  | Access | 3              | —            | Admin laptop |

Switch management: `10.10.1.3` (Infra), gateway `10.10.1.1`

## Preconditions

- Console/physical access available for UXG-Lite and `srv-network`.
- Tailscale reachable on `srv-network` and `srv-media`.
- Recent backups exist for `/srv/config` on `srv-network` and `srv-media`.

## Offline adoption (no WAN connected)

Cabling:
- UXG-Lite LAN → Flex Mini Port 1
- `srv-network` → Flex Mini Port 3
- Admin laptop → Flex Mini Port 5

UniFi configuration (controller on `srv-network.home.arpa`):
- Define VLAN networks per `docs/ipam.md`.
- Set Controller Host/IP Override to `srv-network.home.arpa` (or `10.10.1.10`).
- Apply switch port profile mapping.

Reservations (where applicable):
- `srv-network.home.arpa` → `10.10.1.10`
- `dns-pihole.home.arpa` → `10.10.1.2` (only if using macvlan)
- `sw-flex-5p.home.arpa` → `10.10.1.3`
- `srv-media.home.arpa` → `10.10.2.2`
- (optional) `ap-eero.home.arpa` → `10.10.3.2`

## Cutover cabling

- NTD → UXG-Lite WAN
- UXG-Lite LAN → Flex Mini Port 1
- Unmanaged TPLink 5-port → Flex Mini Port 2
- `srv-network` → Flex Mini Port 3
- eero (Bridge Mode) → Flex Mini Port 4
- Admin laptop → Flex Mini Port 5

## DHCP and DNS

UniFi DHCP:
- Clients VLAN: `10.10.3.50–199`
- DNS: Primary `10.10.1.2`; Secondary unset (until redundancy exists)

Pi-hole:
- Conditional forwarding:
  - Router: `10.10.1.1`
  - Domain: `home.arpa`
  - Local network: `10.10.0.0/16`
- Local DNS A records:
  - `gw-uxg.home.arpa` → `10.10.1.1`
  - `dns-pihole.home.arpa` → `10.10.1.2`
  - `sw-flex-5p.home.arpa` → `10.10.1.3`
  - `srv-network.home.arpa` → `10.10.1.10`
  - `srv-media.home.arpa` → `10.10.2.2`

## Validation checklist

Clients:
- Address in `10.10.3.0/24`, gateway `10.10.3.1`, DNS `10.10.1.2`
- Internet access confirmed
- Pi-hole shows client-level queries

Infra:
- UXG-Lite and Flex Mini connected in UniFi
- Controller override resolves to `srv-network.home.arpa`

Servers:
- `srv-media.home.arpa` resolves via Pi-hole
- SSH reachable by hostname
- Media/download stack reachable via hostname and expected ports

## Rollback

- Disable DHCP on Clients VLAN (UniFi).
- Remove UXG-Lite from path.
- NTD/Modem → eero WAN; set eero to Router Mode.
- Reconnect clients to eero.
- Confirm clients receive `192.168.4.x` leases.
