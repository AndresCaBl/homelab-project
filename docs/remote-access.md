# Remote Access (Tailscale)

## Purpose
Remote admin access without router port forwarding.

## Hosts
- srv-media
- srv-network

Removed:
- lab-proxmox (decommissioned)

## Install (Ubuntu)

curl -fsSL https://tailscale.com/install.sh | sh
sudo systemctl enable --now tailscaled
sudo tailscale up

Verify:
tailscale status
tailscale ip -4

## DNS

Tailscale:
- MagicDNS enabled.
- Hostnames:
  - srv-media.tail401c13.ts.net
  - srv-network.tail401c13.ts.net

LAN:
- Local DNS uses home.arpa:
  - srv-media.home.arpa
  - srv-network.home.arpa

## Access checks

Remote (on Tailscale):
ping srv-media.tail401c13.ts.net
ping srv-network.tail401c13.ts.net
ssh andres@srv-media.tail401c13.ts.net
ssh andres@srv-network.tail401c13.ts.net

LAN (no VPN):
ping srv-media.home.arpa
ping srv-network.home.arpa
ssh andres@srv-media.home.arpa
ssh andres@srv-network.home.arpa

## Notes
- No WAN port forwards.
- If subnet routes or exit nodes are enabled later, record the routes and ACLs.
