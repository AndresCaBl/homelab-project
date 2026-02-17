# SSH Key and Access Setup

## Key generation (WSL)

ssh-keygen -t ed25519 -a 100 -f ~/.ssh/homelab_ed25519 -C "andres@homelab"

Files:
- ~/.ssh/homelab_ed25519 (private)
- ~/.ssh/homelab_ed25519.pub (public)

## Deploy keys

srv-media:
ssh-copy-id -i ~/.ssh/homelab_ed25519.pub andres@srv-media.home.arpa

srv-network:
ssh-copy-id -i ~/.ssh/homelab_ed25519.pub andres@srv-network.home.arpa

## Server-side permissions

chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
chown -R andres:andres ~/.ssh

## Client SSH config (WSL)

File: ~/.ssh/config

Host srv-media
    HostName srv-media.home.arpa
    User andres
    IdentityFile ~/.ssh/homelab_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes

Host srv-network
    HostName srv-network.home.arpa
    User andres
    IdentityFile ~/.ssh/homelab_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes

Host srv-media-ts
    HostName srv-media.tail401c13.ts.net
    User andres
    IdentityFile ~/.ssh/homelab_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes

Host srv-network-ts
    HostName srv-network.tail401c13.ts.net
    User andres
    IdentityFile ~/.ssh/homelab_ed25519
    IdentitiesOnly yes
    AddKeysToAgent yes

## ssh-agent in WSL

Add to ~/.bashrc:

SSH_ENV="$HOME/.ssh/agent-environment"

start_agent() {
    eval "$(ssh-agent -s)" > /dev/null
    ssh-add ~/.ssh/homelab_ed25519
    echo "export SSH_AUTH_SOCK=$SSH_AUTH_SOCK" > "$SSH_ENV"
    echo "export SSH_AGENT_PID=$SSH_AGENT_PID" >> "$SSH_ENV"
    chmod 600 "$SSH_ENV"
}

if [ -f "$SSH_ENV" ]; then
    . "$SSH_ENV" > /dev/null
    if ! kill -0 "$SSH_AGENT_PID" 2>/dev/null; then
        start_agent
    fi
else
    start_agent
fi
