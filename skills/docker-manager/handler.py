#!/usr/bin/env python3
import sys
import os
import subprocess

def run_docker(args, capture=True):
    cmd = ["docker"] + args
    try:
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, check=True)
            return "Command executed"
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}" if e.stderr else f"Error: {e.stdout.strip()}"
    except FileNotFoundError:
        return "Docker not found. Install Docker first."

def docker_compose(args, path="."):
    cmd = ["docker-compose"] + args
    try:
        result = subprocess.run(cmd, cwd=path, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr.strip()}" if e.stderr else f"Error: {e.stdout.strip()}"
    except FileNotFoundError:
        return "docker-compose not found"

def ps():
    return run_docker(["ps", "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"])

def ps_all():
    return run_docker(["ps", "-a", "--format", "table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}"])

def images():
    return run_docker(["images", "--format", "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.ID}}"])

def run_container(image, name=None, detach=True, ports=None, env=None):
    cmd = ["run"]
    if detach:
        cmd.append("-d")
    if name:
        cmd.extend(["--name", name])
    if ports:
        for port in ports:
            cmd.extend(["-p", port])
    if env:
        for e in env:
            cmd.extend(["-e", e])
    cmd.append(image)
    
    return run_docker(cmd)

def stop_container(container):
    return run_docker(["stop", container])

def start_container(container):
    return run_docker(["start", container])

def restart_container(container):
    return run_docker(["restart", container])

def remove_container(container, force=False):
    cmd = ["rm"]
    if force:
        cmd.append("-f")
    cmd.append(container)
    return run_docker(cmd)

def remove_image(image, force=False):
    cmd = ["rmi"]
    if force:
        cmd.append("-f")
    cmd.append(image)
    return run_docker(cmd)

def container_logs(container, tail=50, follow=False):
    cmd = ["logs"]
    if follow:
        cmd.append("-f")
    cmd.extend(["--tail", str(tail)])
    cmd.append(container)
    return run_docker(cmd)

def exec_container(container, command):
    return run_docker(["exec", container, "sh", "-c", command])

def build_image(path, tag):
    return run_docker(["build", "-t", tag, path])

def pull_image(image):
    return run_docker(["pull", image])

def push_image(image):
    return run_docker(["push", image])

def volume_list():
    return run_docker(["volume", "ls", "--format", "table {{.Name}}\t{{.Driver}}\t{{.Mountpoint}}"])

def network_list():
    return run_docker(["network", "ls", "--format", "table {{.Name}}\t{{.Driver}}\t{{.Scope}}"])

def container_stats(container=None, stream=False):
    cmd = ["stats", "--no-stream"]
    if container:
        cmd.append(container)
    return run_docker(cmd)

def system_prune():
    return run_docker(["system", "prune", "-af"])

def inspect_container(container):
    return run_docker(["inspect", container])

def main():
    if len(sys.argv) < 2:
        return """Usage: docker-manager <command> [args]

Container Commands:
  ps               - List running containers
  ps-all           - List all containers
  run <image>     - Run container
  run-d <image>   - Run detached
  stop <container> - Stop container
  start <container> - Start container
  restart <container> - Restart container
  rm <container>  - Remove container
  logs <container> - View logs
  exec <container> <cmd> - Execute command

Image Commands:
  images           - List images
  rmi <image>     - Remove image
  build <path> <tag> - Build image
  pull <image>    - Pull image
  push <image>    - Push image

System Commands:
  volume ls        - List volumes
  network ls      - List networks
  stats           - Show stats
  prune           - Prune system

Compose Commands:
  compose up       - Start services
  compose down     - Stop services"""

    command = sys.argv[1]

    if command == "ps":
        return ps()
    elif command == "ps-all":
        return ps_all()
    elif command == "images":
        return images()
    elif command == "run":
        if len(sys.argv) < 3:
            return "Usage: run <image> [options]"
        return run_container(sys.argv[2])
    elif command == "run-d":
        if len(sys.argv) < 3:
            return "Usage: run-d <image>"
        return run_container(sys.argv[2], detach=True)
    elif command == "stop":
        if len(sys.argv) < 3:
            return "Usage: stop <container>"
        return stop_container(sys.argv[2])
    elif command == "start":
        if len(sys.argv) < 3:
            return "Usage: start <container>"
        return start_container(sys.argv[2])
    elif command == "restart":
        if len(sys.argv) < 3:
            return "Usage: restart <container>"
        return restart_container(sys.argv[2])
    elif command == "rm":
        if len(sys.argv) < 3:
            return "Usage: rm <container>"
        return remove_container(sys.argv[2])
    elif command == "rmi":
        if len(sys.argv) < 3:
            return "Usage: rmi <image>"
        return remove_image(sys.argv[2])
    elif command == "logs":
        if len(sys.argv) < 3:
            return "Usage: logs <container>"
        return container_logs(sys.argv[2])
    elif command == "exec":
        if len(sys.argv) < 4:
            return "Usage: exec <container> <command>"
        return exec_container(sys.argv[2], sys.argv[3])
    elif command == "build":
        if len(sys.argv) < 4:
            return "Usage: build <path> <tag>"
        return build_image(sys.argv[2], sys.argv[3])
    elif command == "pull":
        if len(sys.argv) < 3:
            return "Usage: pull <image>"
        return pull_image(sys.argv[2])
    elif command == "push":
        if len(sys.argv) < 3:
            return "Usage: push <image>"
        return push_image(sys.argv[2])
    elif command == "volume":
        if len(sys.argv) > 2 and sys.argv[2] == "ls":
            return volume_list()
        return "Usage: volume ls"
    elif command == "network":
        if len(sys.argv) > 2 and sys.argv[2] == "ls":
            return network_list()
        return "Usage: network ls"
    elif command == "stats":
        container = sys.argv[2] if len(sys.argv) > 2 else None
        return container_stats(container)
    elif command == "prune":
        return system_prune()
    elif command == "compose":
        if len(sys.argv) < 3:
            return "Usage: compose <up|down>"
        if sys.argv[2] == "up":
            return docker_compose(["up", "-d"])
        elif sys.argv[2] == "down":
            return docker_compose(["down"])
        else:
            return f"Unknown compose command: {sys.argv[2]}"
    elif command == "inspect":
        if len(sys.argv) < 3:
            return "Usage: inspect <container>"
        return inspect_container(sys.argv[2])
    else:
        return f"Unknown command: {command}"

if __name__ == "__main__":
    print(main())
