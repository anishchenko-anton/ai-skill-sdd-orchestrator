# Linux VPS Security Checklist

This checklist must be followed by DevOps agents when provisioning or configuring a new Linux server (e.g., Ubuntu/Debian on a VPS).

---

## 1. User & Access Management
- **Create a Non-Root User**: Never run applications or deploy code as the `root` user. Create a dedicated user (e.g., `deploy` or `ubuntu`) and grant it `sudo` privileges if necessary.
- **SSH Key Authentication**: Enforce SSH key-based authentication. Disable password authentication completely in `/etc/ssh/sshd_config` (`PasswordAuthentication no`).
- **Disable Root SSH Login**: Set `PermitRootLogin no` in the SSH daemon configuration.

## 2. Firewall Configuration (UFW)
Always enable a firewall to block all incoming traffic except what is explicitly required.
- Set default policies: `sudo ufw default deny incoming`, `sudo ufw default allow outgoing`.
- Allow SSH: `sudo ufw allow OpenSSH` (or the custom SSH port if changed).
- Allow HTTP/HTTPS: `sudo ufw allow 80/tcp`, `sudo ufw allow 443/tcp`.
- **Enable UFW**: `sudo ufw enable`.

## 3. Intrusion Prevention
- **Fail2ban**: Install and configure `fail2ban` to protect the SSH port against brute-force attacks. Ensure the service is enabled and running.

## 4. Updates & Maintenance
- **Automatic Security Updates**: Configure `unattended-upgrades` to ensure the OS receives critical security patches automatically without manual intervention.

## 5. Principle of Least Privilege for Services
- Web servers (Nginx) must run as `www-data` or similar unprivileged user.
- Systemd services must specify a non-root `User=` and `Group=` in their `.service` files.
