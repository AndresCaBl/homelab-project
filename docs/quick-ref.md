# Homelab Quick Reference

## Core Services (srv-media)
- Cockpit: https://192.168.4.90:9090
  - Health: curl -kI https://127.0.0.1:9090/ → 200/302
- Jellyfin: http://192.168.4.90:8096   (/health)
- Plex: http://192.168.4.90:32400/web  (/identity)
- Sonarr: http://192.168.4.90:8989     (/ping)
- Radarr: http://192.168.4.90:7878     (/ping)
- Bazarr: http://192.168.4.90:6767
- Jellyseerr: http://192.168.4.90:5055
- qBittorrent (via Gluetun): http://192.168.4.90:8080
- Prowlarr (via Gluetun): http://192.168.4.90:9696
- FlareSolverr (via Gluetun): http://192.168.4.90:8191
- Homepage dashboard: http://192.168.4.90:3000

## System Info
- SSH: andres@srv-media (192.168.4.90)
- Reserved IPs:
  - srv-media → 192.168.4.90
  - lab-proxmox → 192.168.4.91
- DNS: Pi-hole planned (Phase 8) → .home domain

## Health Checks
- CPU/mem/disk: Cockpit (PCP)
- Updates: Cockpit → Software Updates / `apt update && apt full-upgrade -y`
- SMART status: `smartctl -a /dev/sdX`
- Temps: `sensors`
