# Docker Setup — Ubuntu

Host: **Desktop PC (simulated branch office)**   
OS: **Ubuntu 24.04 LTS**

---

### 1) Install Docker & Compose plugin (Ubuntu repo)

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
```
*This uses Ubuntu’s maintained packages (docker.io) rather than Docker CE.*
<br>

### 2) (Optional) Run Docker without sudo

Add your user to the docker group and refresh group membership:

```bash
sudo usermod -aG docker $USER
# log out and back in (to refresh groups), or run:
newgrp docker
```
Quick sanity check (should not require sudo after the group refresh):
```bash
docker ps
```

### 3) Verify Docker is working
```bash
docker --version
docker compose version 2>/dev/null || docker-compose --version 2>/dev/null || echo "Compose plugin not found"
```
Run the classic test container and remove it after exit:
```bash
docker run --rm hello-world
```
If you see the hello‑world message, Docker is functioning correctly.

### 4) (Optional) Basic service checks
```bash
# Check service status
systemctl status docker --no-pager

# Enable at boot (usually enabled by the package, but harmless to run)
sudo systemctl enable --now docker
```
### 5) Quick cheatsheet
#### Containers
```bash
docker ps                    # running containers
docker ps -a                 # all containers
docker logs -f <name>        # follow logs
docker exec -it <name> bash  # shell into container
docker stop <name>           # stop
docker start <name>          # start
docker rm <name>             # remove (stopped)
```
#### Images & cleanup
```bash
docker images                # list all downloaded images
docker rmi <image>           # remove a specific image by name or ID
docker system df             # show disk space used by images, containers, volumes
docker system prune -f       # clean up unused images/containers/networks (force, careful)
```
#### Compose plugin
```bash
docker compose up -d         # start services in detached mode (from compose.yaml)
docker compose ps            # list running services defined by compose
docker compose down          # stop and remove services/containers from compose.yaml
```
---
✅ Docker is now installed and verified on the Desktop PC.  
Next: deploy containers (e.g., MariaDB) as part of the Cyberlab branch-office simulation.
