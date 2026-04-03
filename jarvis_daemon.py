#!/usr/bin/env python3
"""JARVIS Persistent Daemon - Keep JARVIS alive forever.

Runs as a background service, keeps all systems initialized,
enables continuous vision, memory, and autonomous behavior.

Author: J.A.R.V.I.S.
"""
import os
import sys
import time
import json
import signal
import subprocess
import threading
import socket
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import socket


class JarviSDaemon:
    """Persistent JARVIS daemon."""
    
    def __init__(self, port: int = 54321):
        self.port = port
        self.running = False
        self.pid_file = "/tmp/jarvis_daemon.pid"
        self.state_file = "/tmp/jarvis_state.json"
        
        # Core systems
        self.vision = None
        self.memory = None
        self.auto_engine = None
        self.self_healer = None
        self.os_specialist = None
        self.sudo_manager = None
        
        # State
        self.start_time = time.time()
        self.cycle_count = 0
        self.uptime = "0s"
        
    def _load_core_systems(self):
        """Load all core JARVIS systems."""
        print("[JARVIS] Initializing core systems...")
        
        # Add JARVIS to path
        base_dir = "/home/mirza/Desktop/J.A.R.V.I.S"
        sys.path.insert(0, base_dir)
        
        # Initialize systems
        try:
            from jarvis_vision import jarvis_eyes
            self.vision = jarvis_eyes
            print("[JARVIS] ✓ Vision (Eyes) loaded")
        except Exception as e:
            print(f"[JARVIS] ✗ Vision failed: {e}")
        
        try:
            from infinite_memory import infinite_memory
            self.memory = infinite_memory
            print("[JARVIS] ✓ Memory (Infinite) loaded")
        except Exception as e:
            print(f"[JARVIS] ✗ Memory failed: {e}")
        
        try:
            from autonomous_engine import engine as auto_engine
            self.auto_engine = auto_engine
            print("[JARVIS] ✓ Autonomous Engine loaded")
        except Exception as e:
            print(f"[JARVIS] ✗ Autonomous Engine failed: {e}")
        
        try:
            from self_healer import self_healer
            self.self_healer = self_healer
            print("[JARVIS] ✓ Self-Healer loaded")
        except Exception as e:
            print(f"[JARVIS] ✗ Self-Healer failed: {e}")
        
        try:
            from os_specialist import os_specialist
            self.os_specialist = os_specialist
            print("[JARVIS] ✓ OS Specialist loaded")
        except Exception as e:
            print(f"[JARVIS] ✗ OS Specialist failed: {e}")
        
        try:
            from sudo_manager import sudo_manager
            self.sudo_manager = sudo_manager
            # Auto-authenticate sudo
            sudo_manager.authenticate()
            print("[JARVIS] ✓ Sudo Manager loaded")
        except Exception as e:
            print(f"[JARVIS] ✗ Sudo Manager failed: {e}")
        
        print("[JARVIS] Core systems initialized!")
    
    def _start_background_tasks(self):
        """Start background monitoring tasks."""
        # Start autonomous engine monitoring
        if self.auto_engine:
            if not self.auto_engine.running:
                threading.Thread(
                    target=lambda: asyncio.run(self.auto_engine.start(60)),
                    daemon=True
                ).start()
                print("[JARVIS] Autonomous monitoring started")
        
        # Start vision if camera available
        if self.vision:
            try:
                self.vision.enable("/dev/video0")
                print("[JARVIS] Vision enabled - JARVIS is watching")
            except Exception as e:
                print(f"[JARVIS] Vision enable failed: {e}")
        
        # Start self-healer monitoring
        if self.self_healer:
            self.self_healer.start_monitoring()
            print("[JARVIS] Self-healer monitoring started")
    
    def _save_state(self):
        """Save daemon state."""
        uptime_seconds = int(time.time() - self.start_time)
        hours = uptime_seconds // 3600
        minutes = (uptime_seconds % 3600) // 60
        seconds = uptime_seconds % 60
        
        state = {
            "running": self.running,
            "start_time": datetime.fromtimestamp(self.start_time).isoformat(),
            "uptime": f"{hours}h {minutes}m {seconds}s",
            "cycle_count": self.cycle_count,
            "systems": {
                "vision": self.vision is not None and getattr(self.vision, '_enabled', False),
                "memory": self.memory is not None,
                "autonomous": self.auto_engine is not None and getattr(self.auto_engine, 'running', False),
                "self_healer": self.self_healer is not None,
                "os_specialist": self.os_specialist is not None,
            },
            "timestamp": datetime.now().isoformat()
        }
        
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _handle_client(self, client_sock):
        """Handle client connection."""
        try:
            data = client_sock.recv(4096)
            if not data:
                return
            
            request = json.loads(data.decode())
            command = request.get("command", "")
            args = request.get("args", [])
            
            response = self._execute_command(command, args)
            
            client_sock.send(json.dumps(response).encode())
        except Exception as e:
            client_sock.send(json.dumps({"error": str(e)}).encode())
        finally:
            client_sock.close()
    
    def _execute_command(self, command: str, args: list) -> Dict:
        """Execute command and return response."""
        self.cycle_count += 1
        
        if command == "ping":
            return {"status": "ok", "message": "JARVIS is alive!", "uptime": self.uptime}
        
        elif command == "status":
            return {
                "status": "ok",
                "systems": {
                    "vision": self.vision is not None,
                    "vision_enabled": self.vision._enabled if self.vision else False,
                    "memory": self.memory is not None,
                    "autonomous": self.auto_engine.running if self.auto_engine else False,
                },
                "uptime": self.uptime
            }
        
        elif command == "observe" or command == "see":
            if self.vision and self.vision._enabled:
                return {"status": "ok", "observation": self.vision.observe()}
            return {"status": "error", "message": "Vision not enabled"}
        
        elif command == "remember":
            if args:
                text = " ".join(args)
                if self.memory:
                    id_ = self.memory.remember_everything(text)
                    return {"status": "ok", "memory_id": id_, "text": text[:50]}
            return {"status": "error", "message": "No text provided"}
        
        elif command == "recall":
            query = " ".join(args) if args else ""
            if self.memory:
                results = self.memory.recall_human_style(query)
                return {"status": "ok", "results": results}
            return {"status": "error", "message": "Memory not loaded"}
        
        elif command == "health":
            if self.self_healer:
                report = self.self_healer.get_health_report()
                return {"status": "ok", "report": report}
            return {"status": "error", "message": "Self-healer not loaded"}
        
        elif command == "repair":
            if self.self_healer:
                results = self.self_healer.auto_repair_all()
                return {"status": "ok", "results": results}
            return {"status": "error", "message": "Self-healer not loaded"}
        
        elif command == "os":
            if self.os_specialist:
                info = self.os_specialist.get_os_info()
                return {"status": "ok", "os": info}
            return {"status": "error", "message": "OS specialist not loaded"}
        
        elif command == "check_alerts":
            if self.auto_engine:
                return {"status": "ok", "alerts": self.auto_engine.get_summary()}
            return {"status": "error", "message": "Autonomous engine not loaded"}
        
        elif command == "enable_vision":
            if self.vision:
                self.vision.enable("/dev/video0")
                return {"status": "ok", "message": "Vision enabled"}
            return {"status": "error", "message": "Vision not available"}
        
        elif command == "disable_vision":
            if self.vision:
                self.vision.disable()
                return {"status": "ok", "message": "Vision disabled"}
            return {"status": "error", "message": "Vision not available"}
        
        elif command == "shell":
            if args:
                cmd = " ".join(args)
                if self.sudo_manager:
                    success, output = self.sudo_manager.execute(cmd)
                    return {"status": "ok" if success else "error", "output": output[:1000]}
            return {"status": "error", "message": "No command provided"}
        
        elif command == "help":
            return {"status": "ok", "commands": [
                "ping", "status", "observe", "remember <text>", "recall <query>",
                "health", "repair", "os", "check_alerts", "enable_vision", 
                "disable_vision", "shell <command>"
            ]}
        
        return {"status": "error", "message": f"Unknown command: {command}"}
    
    def start(self):
        """Start the daemon."""
        # Check if already running
        if os.path.exists(self.pid_file):
            with open(self.pid_file) as f:
                old_pid = int(f.read().strip())
            try:
                os.kill(old_pid, 0)
                print(f"JARVIS daemon already running (PID: {old_pid})")
                return False
            except OSError:
                pass
        
        # Write PID
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
        
        self.running = True
        print(f"[JARVIS] Daemon starting on port {self.port}...")
        
        # Load systems
        self._load_core_systems()
        
        # Start background tasks
        self._start_background_tasks()
        
        # Create socket server
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(('127.0.0.1', self.port))
        server.listen(5)
        
        print(f"[JARVIS] Daemon running! PID: {os.getpid()}")
        print(f"[JARVIS] Socket server listening on 127.0.0.1:{self.port}")
        print("[JARVIS] Type 'jarvis-ctl status' to check")
        
        # Main loop
        while self.running:
            try:
                server.settimeout(1.0)
                try:
                    client, addr = server.accept()
                    threading.Thread(
                        target=self._handle_client,
                        args=(client,),
                        daemon=True
                    ).start()
                except socket.timeout:
                    pass
                
                # Update state every 10 cycles
                self.cycle_count += 1
                if self.cycle_count % 10 == 0:
                    self._save_state()
                    uptime_seconds = int(time.time() - self.start_time)
                    hours = uptime_seconds // 3600
                    minutes = (uptime_seconds % 3600) // 60
                    self.uptime = f"{hours}h {minutes}m"
                
            except Exception as e:
                print(f"[JARVIS] Error: {e}")
                break
        
        server.close()
        return True
    
    def stop(self):
        """Stop the daemon."""
        self.running = False
        
        # Disable vision
        if self.vision:
            self.vision.disable()
        
        # Stop auto engine
        if self.auto_engine:
            self.auto_engine.stop()
        
        # Stop self-healer
        if self.self_healer:
            self.self_healer.stop_monitoring()
        
        # Remove PID file
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)
        
        print("[JARVIS] Daemon stopped")


# Control script
def main():
    if len(sys.argv) < 2:
        print("Usage: jarvis_daemon.py <command>")
        print("\nCommands:")
        print("  start   - Start JARVIS daemon")
        print("  stop    - Stop JARVIS daemon")
        print("  status  - Check daemon status")
        print("  shell   - Run shell command via daemon")
        print("  ping    - Ping JARVIS")
        sys.exit(1)
    
    cmd = sys.argv[1]
    port = 54321
    
    if cmd == "start":
        import asyncio
        daemon = JarviSDaemon()
        daemon.start()
    
    elif cmd == "stop":
        # Send stop signal via socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', port))
            sock.send(json.dumps({"command": "stop"}).encode())
            sock.close()
        except:
            # Just kill by PID
            if os.path.exists("/tmp/jarvis_daemon.pid"):
                with open("/tmp/jarvis_daemon.pid") as f:
                    pid = int(f.read())
                try:
                    os.kill(pid, signal.SIGTERM)
                    print("JARVIS daemon stopped")
                except:
                    print("Could not stop daemon")
    
    elif cmd == "status":
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', port))
            sock.send(json.dumps({"command": "status"}).encode())
            response = sock.recv(4096)
            sock.close()
            print(json.dumps(json.loads(response), indent=2))
        except:
            print("JARVIS daemon not running")
    
    elif cmd == "ping":
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', port))
            sock.send(json.dumps({"command": "ping"}).encode())
            response = sock.recv(4096)
            sock.close()
            print(json.loads(response).get("message", "No response"))
        except:
            print("JARVIS not responding")
    
    elif cmd == "shell":
        if len(sys.argv) < 3:
            print("Usage: jarvis_daemon.py shell <command>")
            sys.exit(1)
        cmd = " ".join(sys.argv[2:])
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(('127.0.0.1', port))
            sock.send(json.dumps({"command": "shell", "args": [cmd]}).encode())
            response = sock.recv(8192)
            sock.close()
            result = json.loads(response)
            print(result.get("output", result.get("message", "")))
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()
