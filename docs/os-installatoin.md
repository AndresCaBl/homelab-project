# OS Installation & Baseline Hardening

## Hosts (current)

- srv-media — Ubuntu Server 24.04.3 LTS
- srv-network — Ubuntu Server (runs UniFi Network Application + Pi-hole in Docker)

Removed:
- lab-proxmox (decommissioned)

Historical:
- old-dell — Ubuntu Desktop 24.04 (migration source)

## Install Notes

- Hostnames set during install:
  - srv-media
  - srv-network
- Local admin user created: andres (sudo).
- Networking:
  - Prefer Ethernet for lab hosts.
  - Current addressing/DNS is defined in docs/ipam.md (UniFi VLANs and home.arpa).

## Post-Install Steps

- Updates and base tooling

  sudo apt update && sudo apt full-upgrade -y
  sudo apt install -y vim curl htop net-tools

- SSH

  sudo apt install -y openssh-server
  sudo systemctl enable --now ssh

- Disabled suspend on lid close:

  sudo nano /etc/systemd/logind.conf
  # Set:
  HandleLidSwitch=ignore
  HandleLidSwitchDocked=ignore
  # Then restart service:
  sudo systemctl restart systemd-logind
