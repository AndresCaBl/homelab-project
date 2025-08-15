# OS Installation & Baseline Hardening

## Host OS Summary
- **srv-media**: Ubuntu Server 24.04.3 LTS
- **lab-proxmox**: Proxmox VE 9.0-1
- **old-dell**: Ubuntu Desktop 24.04 (migration source server)

## Install Notes
- Verified ISO checksums before installation.
- Disabled Secure Boot in BIOS for Proxmox host.
- **srv-media**: default LVM partitioning.
- **lab-proxmox**: ZFS root setup during install.
- Hostnames set during install:
  - `srv-media`
  - `lab-proxmox`
- Network config:
  - Static IPs assigned via Eero router DHCP reservation.
  - Wi-Fi disabled on both main servers; Ethernet used for stability.
- Local user created: `andres` (sudo privileges).

## Post-Install Steps
- Applied full system updates:
  ```bash
    sudo apt update && sudo apt full-upgrade -y
    sudo apt install -y vim curl htop net-tools
    
- Enabled SSH
    sudo apt install -y openssh-server
    sudo systemctl enable --now ssh

- Disabled suspend on lid close:

    sudo nano /etc/systemd/logind.conf
    # Set:
    HandleLidSwitch=ignore
    HandleLidSwitchDocked=ignore
    # Then restart service:
    sudo systemctl restart systemd-logind