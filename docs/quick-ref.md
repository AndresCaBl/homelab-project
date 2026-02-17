# Homelab Quick Reference

## Hosts
- `srv-network.home.arpa` (Infra) — UniFi Network Application + Pi-hole (Docker)
- `srv-media.home.arpa` (Servers) — media + automation host

## Addresses
- `srv-network.home.arpa` → `10.10.1.10`
- `dns-pihole.home.arpa` → `10.10.1.2`
- `srv-media.home.arpa` → `10.10.2.2`

## Core Services (srv-media)
- Cockpit: https://srv-media.home.arpa:9090
  - Health: `curl -kI https://127.0.0.1:9090/` → 200/302
- Jellyfin: http://srv-media.home.arpa:8096  (`/health`)
- Plex: http://srv-media.home.arpa:32400/web  (`/identity`)
- Sonarr: http://srv-media.home.arpa:8989  (`/ping`)
- Radarr: http://srv-media.home.arpa:7878  (`/ping`)
- Bazarr: http://srv-media.home.arpa:6767
- Jellyseerr: http://srv-media.home.arpa:5055
- qBittorrent (via Gluetun): http://srv-media.home.arpa:8080
- Prowlarr (via Gluetun): http://srv-media.home.arpa:9696
- FlareSolverr (via Gluetun): http://srv-media.home.arpa:8191
- Homepage: http://srv-media.home.arpa:3000

## Admin access
- SSH: `andres@srv-media.home.arpa` (`10.10.2.2`)

## Health Checks
- CPU/mem/disk: Cockpit
- Updates: `apt update && apt full-upgrade -y`
- SMART status: `smartctl -a /dev/sdX`
- Temps: `sensors`
