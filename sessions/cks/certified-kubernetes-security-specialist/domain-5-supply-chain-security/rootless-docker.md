# rootless docker install 


### Install
```sh
curl -fsSL https://get.docker.com/rootless | sh
```
The installer will output environment variables to add to your shell for the user want to run container.

```sh
# Add to ~/.bashrc or ~/.zshrc
# These configure Docker CLI to connect to rootless daemon
export PATH=/home/$USER/bin:$PATH                        # Add rootless binaries to PATH
export DOCKER_HOST=unix:///run/user/$(id -u)/docker.sock # Point to user-owned socket
```
reload shell

```sh
# Apply the configuration changes
source ~/.bashrc
```
### restart,stop operations
```sh
# Enable daemon to start automatically when you log in
systemctl --user enable docker

# Start the daemon now
systemctl --user start docker

# Check daemon status
systemctl --user status docker

# View daemon logs for troubleshooting
journalctl --user -u docker
```

### verify rootless operation
```sh
# Check Docker info for rootless indicator
docker info | grep -i rootless
# Should show: rootless

# Verify the daemon socket path is user-owned
echo $DOCKER_HOST
# Should be: unix:///run/user/<uid>/docker.sock

# Run container and check UID inside
docker run --rm alpine id
# Shows: uid=0(root) - this is root INSIDE the container

# View the UID mapping to confirm container root maps to your UID
docker run --rm alpine cat /proc/1/uid_map
# Shows mapping: 0 <your-uid> 1
# This means container UID 0 maps to your host UID
```

