# Home Lab Project

This repository tracks the infrastructure-as-code, configurations, and runbooks for a two-node home lab.

## Goals
- Media Server: Automate Plex library management using sonarr/radarr/overseerr
- Migration-friendly: All data/config under `/srv/*` on hosts
- Everything-as-Code: Docker Compose, env templates (no secrets)
- Learning-aligned: Maps to AZ-900/104/204 and CCNA objectives

## Structure
- `docs/` — network plan, decisions, runbooks, diagrams
- `compose/` — docker-compose projects (media, downloads, monitoring)
- `config/` — app configs that are safe to version
- `bin/` — helper scripts (bash)
- `backup/` — backup scripts and docs (no archives checked in)

## Phases
See `docs/runbook.md` and `docs/decisions.md`.
