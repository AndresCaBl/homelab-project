# Home Lab Project

This repo tracks the configs and runbooks for my home lab. The focus is repeatable builds, clean migrations, and day-to-day ops.

## Goals

- Media server: Plex-first with automated library management (Sonarr/Radarr) and requests (Jellyseerr)
- Migration-friendly: persistent data under `/srv/*`
- Everything as code: Docker Compose with `.env.example` templates - Practice for IaC automation and deployments.
- Learning-aligned: practical networking and operations work aligned to AZ-900/AZ-104/AZ-204 and CCNA

## Current environment (summary)

- Domain: `home.arpa`
- Network: UniFi UXG-Lite with VLANs (see `docs/ipam.md`)
- DNS: Pi-hole on `srv-network.home.arpa` (Docker)
- Hosts:
  - `srv-network` — UniFi Network Application + Pi-hole
  - `srv-media` — media + automation (Ubuntu Server 24.04.3 LTS)

## Services (srv-media)

- Plex (primary), Jellyfin (secondary)
- Sonarr, Radarr, Bazarr, Jellyseerr
- qBittorrent + Prowlarr + FlareSolverr behind Gluetun

## Structure

- `docs/` — IPAM, ADRs, runbooks, diagrams
- `compose/` — docker-compose projects
- `config/` — version-safe app configs
- `bin/` — helper scripts
- `backup/` — backup scripts and notes (no archives committed)

## Docs

- `docs/ipam.md` — VLANs, addressing, hostnames
- `docs/runbook.md` — build phases and operating notes
- `docs/decisions.md` — ADR log
- `docs/quick-ref.md` — service endpoints and common checks
