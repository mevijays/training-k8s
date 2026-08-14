# Question 14: Restrict Docker Engine Access

## Objective

- Remove only user `developer` from group `docker`.
- Make `/var/run/docker.sock` owned by group `root`.
- Ensure Docker does not listen on any TCP port.
- Restart Docker and confirm Kubernetes remains healthy.

The Docker group effectively grants root-level control, so membership must be treated as privileged access.

## What this lab does and why

**What we are doing:** We are removing one user's privileged Docker access, restricting the daemon to a root-owned local Unix socket, and eliminating TCP listeners. We inspect both systemd and `daemon.json` because either location can control Docker's socket and network bindings.

**Why it matters:** Members of the Docker group can create privileged containers and mount the host filesystem, which is effectively root access. An exposed Docker TCP API can provide the same control remotely, especially when it is unauthenticated. Restricting the socket and listeners reduces both local and network attack surfaces.

**Objective summary:** Only root can access the local Docker socket, `developer` retains all unrelated group memberships, no Docker API port is listening, and Kubernetes remains healthy after restart.

## Concept and theory

- **Daemon privilege:** The Docker daemon normally runs as root and can create privileged containers, mount arbitrary host paths, and control host networking. Access to its API is therefore equivalent to highly privileged host access.
- **Unix socket authorization:** `/var/run/docker.sock` is the local API endpoint. Unix ownership and mode bits determine which local users can open it. Membership in the socket's group commonly bypasses the need for `sudo`, which is why the `docker` group is considered root-equivalent.
- **TCP exposure:** A `tcp://` listener exposes the daemon API beyond filesystem permissions. An unauthenticated port such as 2375 is especially dangerous; even TLS-enabled remote access should exist only when explicitly required and strongly authenticated.
- **Configuration sources:** Docker can receive host and group settings from command-line flags, `daemon.json`, `docker.service`, or `docker.socket`. Defining the same option in multiple sources can prevent the daemon from starting, so the effective systemd unit must be inspected before editing.
- **Runtime dependency:** On a Docker-backed Kubernetes node, restarting Docker temporarily affects the containers kubelet manages. The final health check confirms the runtime returned and Kubernetes reconciled its node and Pods successfully.

## Record the current state

```bash
id developer
getent group docker
stat -c 'owner=%U group=%G mode=%a path=%n' /var/run/docker.sock
sudo systemctl cat docker.service
sudo systemctl cat docker.socket
sudo cat /etc/docker/daemon.json 2>/dev/null || true
sudo ss -lntp | grep dockerd || true
ps -ef | grep '[d]ockerd'
```

Back up the relevant configuration:

```bash
sudo mkdir -p /root/cks-backup/docker
sudo cp -a /etc/docker/daemon.json /root/cks-backup/docker/ 2>/dev/null || true
sudo cp -a /etc/systemd/system/docker.service.d /root/cks-backup/docker/ 2>/dev/null || true
sudo cp -a /etc/systemd/system/docker.socket.d /root/cks-backup/docker/ 2>/dev/null || true
```

## Remove only the Docker group membership

Debian/Ubuntu:

```bash
sudo gpasswd -d developer docker
```

RHEL-family alternative:

```bash
sudo gpasswd -d developer docker
```

Verify other supplementary groups remain:

```bash
id developer
getent group docker
```

Existing login sessions retain their old supplementary group list. The user must log out, or the session must be terminated, before the removal is fully effective.

## Configure only a root-owned Unix socket

First determine whether host bindings come from `daemon.json`, `docker.service`, or `docker.socket`. Do not configure the same `hosts` option in both daemon flags and `daemon.json`; Docker treats that as a conflict.

### Option A: daemon.json owns the host configuration

Merge these keys into the existing JSON without deleting unrelated settings:

```json
{
  "group": "root",
  "hosts": ["unix:///var/run/docker.sock"]
}
```

Validate JSON:

```bash
sudo dockerd --validate --config-file=/etc/docker/daemon.json
```

If the packaged systemd unit already passes `-H fd://`, remove that flag with a service override so `hosts` is not configured twice:

```ini
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd
```

Create the override with:

```bash
sudo systemctl edit docker.service
```

### Option B: systemd owns the host configuration

Remove all `-H tcp://...` arguments and configure only the Unix socket plus root group:

```ini
[Service]
ExecStart=
ExecStart=/usr/bin/dockerd --group=root -H unix:///var/run/docker.sock
```

Preserve any required package-specific arguments visible in the original `ExecStart`.

If `docker.socket` is active, set its socket group:

```bash
sudo systemctl edit docker.socket
```

```ini
[Socket]
SocketGroup=root
SocketMode=0660
```

## Restart and verify

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker.socket 2>/dev/null || true
sudo systemctl restart docker
sudo systemctl --no-pager --full status docker
```

Verify ownership and listeners:

```bash
stat -c 'owner=%U group=%G mode=%a path=%n' /var/run/docker.sock
sudo ss -lntp | grep dockerd || echo 'No Docker TCP listener'
ps -ef | grep '[d]ockerd'
sudo docker info >/dev/null && echo 'Docker healthy'
```

Expected socket ownership is normally `root:root` with mode `660`; no `tcp://` listener or ports `2375`/`2376` should appear.

Finally verify Kubernetes:

```bash
kubectl get nodes
kubectl get pods -A
```

## Sources

- [Docker daemon CLI and socket options](https://docs.docker.com/reference/cli/dockerd/)
- [Docker remote access warning](https://docs.docker.com/engine/daemon/remote-access/)
- [Docker group security warning](https://docs.docker.com/engine/install/linux-postinstall/)

---

[← Previous: Question 13](13-restricted-pod-security.md) · [Index](README.md) · [Next: Question 15 →](15-istio-strict-mtls.md)
