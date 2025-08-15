# SSH Key & Access Setup

## Key Generation (WSL client)

    ssh-keygen -t ed25519 -a 100 -f ~/.ssh/homelab_ed25519 -C "andres@homelab"

- Saved to ~/.ssh/homelab_ed25519 (private) and ~/.ssh/homelab_ed25519.pub(public).

- Private key is encrypted with a passphrase.

## Deploying Keys to Hosts

    ssh-copy-id -i ~/.ssh/homelab_ed25519.pub andres@srv-media
    ssh-copy-id -i ~/.ssh/homelab_ed25519.pub andres@lab-proxmox
    ssh-copy-id -i ~/.ssh/homelab_ed25519.pub andres@old-dell

- Permissions Checklist (server side)

    chmod 700 ~/.ssh
    chmod 600 ~/.ssh/authorized_keys
    chown -R andres:andres ~/.ssh

## SSH Config (client in WSL)

~/.ssh/config:

    Host srv-media
        HostName 192.168.4.90
        User andres
        IdentityFile ~/.ssh/homelab_ed25519
        IdentitiesOnly yes
        AddKeysToAgent yes

    Host lab-proxmox
        HostName 192.168.4.91
        User andres
        IdentityFile ~/.ssh/homelab_ed25519
        IdentitiesOnly yes
        AddKeysToAgent yes

    Host old-dell
        HostName 192.168.4.92
        User andres
        IdentityFile ~/.ssh/homelab_ed25519
        IdentitiesOnly yes
        AddKeysToAgent yes

## Auto-Start ssh-agent in WSL

- Add to ~/.bashrc:

SSH_ENV="$HOME/.ssh/agent-environment"

    start_agent() {
        echo "Starting ssh-agent..."
        eval "$(ssh-agent -s)" > /dev/null
        ssh-add ~/.ssh/homelab_ed25519
        echo "export SSH_AUTH_SOCK=$SSH_AUTH_SOCK" > "$SSH_ENV"
        echo "export SSH_AGENT_PID=$SSH_AGENT_PID" >> "$SSH_ENV"
        chmod 600 "$SSH_ENV"
    }

    if [ -f "$SSH_ENV" ]; then
        source "$SSH_ENV" > /dev/null
        if ! kill -0 "$SSH_AGENT_PID" 2>/dev/null; then
            start_agent
        fi
    else
        start_agent
    fi
