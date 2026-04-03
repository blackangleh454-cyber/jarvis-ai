# Docker Manager

**Description:** Manage Docker containers, images, volumes, and networks. Build, run, stop, and deploy containers.

**Commands:**
- `ps` - List running containers
- `ps-all` - List all containers
- `images` - List images
- `run <image>` - Run container
- `run-d <image>` - Run detached
- `stop <container>` - Stop container
- `start <container>` - Start container
- `restart <container>` - Restart container
- `rm <container>` - Remove container
- `rmi <image>` - Remove image
- `logs <container>` - View logs
- `exec <container> <cmd>` - Execute command
- `build <path> <tag>` - Build image
- `pull <image>` - Pull image
- `push <image>` - Push to registry
- `volume ls` - List volumes
- `network ls` - List networks
- `compose up` - Docker Compose up
- `compose down` - Docker Compose down

**Usage:**
```bash
python handler.py ps
python handler.py run-d nginx
python handler.py exec webserver bash
python handler.py build . myapp:latest
python handler.py compose up -d
```
