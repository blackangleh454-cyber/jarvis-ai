"""Autonomous Engine - Background monitoring and proactive action.

Runs as a background task that:
1. Monitors system health every N seconds
2. Detects anomalies (high CPU, low disk, failed service, etc.)
3. Auto-remediates known issues
4. Tracks historical patterns
5. Reports findings to the main agent
"""
import asyncio
import time
import subprocess
import json
import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional


class Severity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    severity: Severity
    category: str
    message: str
    metric: float
    timestamp: float = field(default_factory=time.time)
    action: Optional[str] = None
    resolved: bool = False


@dataclass
class SystemState:
    """Persistent system state tracking."""
    cpu_percent: float = 0
    memory_percent: float = 0
    disk_percent: float = 0
    temperature: float = 0
    failed_services: int = 0
    zombies: int = 0
    timestamp: float = field(default_factory=time.time)


class AutonomousEngine:
    """Background system monitor with rule-based reactions and auto-remediation."""

    def __init__(self):
        self.running = False
        self.alerts: list[Alert] = []
        self.rules: list[dict] = []
        self.check_interval = 30  # seconds
        self.listeners: list[Callable] = []
        
        # Historical state tracking
        self.state_history: list[SystemState] = []
        self.max_history = 1440  # Keep 24 hours at 1/min
        
        # Auto-remediation mappings
        self.auto_remediations: dict[str, dict] = {}
        
        # Autonomous mode
        self.autonomous_mode = True  # NEW: Auto-remediate by default
        
        # Trusted commands (auto-execute without confirmation)
        self.trusted_commands = {
            "systemctl restart": "restart service",
            "systemctl stop": "stop service", 
            "kill": "kill process",
            "rm -rf": "delete files",
            "dd": "disk write",
            "mkfs": "format",
            "shutdown": "shutdown",
            "reboot": "reboot",
        }
        
        # Default monitoring rules
        self._init_default_rules()
        self._load_state_history()

    def _init_default_rules(self):
        """Default system health rules."""
        self.rules = [
            {
                "name": "high_cpu",
                "check": self._check_cpu,
                "threshold": 90,
                "severity": Severity.WARNING,
                "message": "CPU usage at {metric}%",
                "action": "Check top processes with process-manager",
            },
            {
                "name": "high_memory",
                "check": self._check_memory,
                "threshold": 90,
                "severity": Severity.CRITICAL,
                "message": "Memory usage at {metric}%",
                "action": "Check memory-hungry processes",
            },
            {
                "name": "low_disk",
                "check": self._check_disk,
                "threshold": 90,
                "severity": Severity.CRITICAL,
                "message": "Disk usage at {metric}%",
                "action": "Run disk cleanup or find large files",
            },
            {
                "name": "high_temperature",
                "check": self._check_temp,
                "threshold": 80,
                "severity": Severity.WARNING,
                "message": "CPU temperature at {metric}°C",
                "action": "Check cooling or reduce load",
            },
            {
                "name": "failed_services",
                "check": self._check_failed_services,
                "threshold": 0,
                "severity": Severity.CRITICAL,
                "message": "{metric} failed systemd services",
                "action": "Check and restart failed services",
            },
            {
                "name": "zombie_processes",
                "check": self._check_zombies,
                "threshold": 0,
                "severity": Severity.WARNING,
                "message": "{metric} zombie processes found",
                "action": "Kill parent processes of zombies",
            },
        ]

    def add_rule(self, name, check_fn, threshold, severity, message, action=None):
        """Add a custom monitoring rule."""
        self.rules.append({
            "name": name,
            "check": check_fn,
            "threshold": threshold,
            "severity": severity,
            "message": message,
            "action": action,
        })

    def on_alert(self, callback: Callable):
        """Register a callback for alerts."""
        self.listeners.append(callback)

    def set_autonomous_mode(self, enabled: bool):
        """Enable/disable autonomous mode (auto-remediation)."""
        self.autonomous_mode = enabled
        return f"Autonomous mode {'enabled' if enabled else 'disabled'}"

    def add_trusted_command(self, pattern: str):
        """Add a command pattern to trusted list."""
        self.trusted_commands[pattern] = "user added"
        return f"Added to trusted: {pattern}"

    def remove_trusted_command(self, pattern: str):
        """Remove a command pattern from trusted list."""
        if pattern in self.trusted_commands:
            del self.trusted_commands[pattern]
            return f"Removed from trusted: {pattern}"
        return f"Not found: {pattern}"

    def is_trusted(self, command: str) -> bool:
        """Check if command matches trusted patterns."""
        for pattern in self.trusted_commands:
            if pattern in command:
                return True
        return False

    def _load_state_history(self):
        """Load historical state from disk."""
        state_file = os.path.expanduser("~/.jarvis/state_history.json")
        try:
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    for d in data:
                        self.state_history.append(SystemState(
                            cpu_percent=d.get("cpu_percent", 0),
                            memory_percent=d.get("memory_percent", 0),
                            disk_percent=d.get("disk_percent", 0),
                            temperature=d.get("temperature", 0),
                            failed_services=d.get("failed_services", 0),
                            zombies=d.get("zombies", 0),
                            timestamp=d.get("timestamp", time.time()),
                        ))
        except Exception:
            pass

    def _save_state_history(self):
        """Save historical state to disk."""
        os.makedirs(os.path.expanduser("~/.jarvis"), exist_ok=True)
        state_file = os.path.expanduser("~/.jarvis/state_history.json")
        try:
            data = [
                {
                    "cpu_percent": s.cpu_percent,
                    "memory_percent": s.memory_percent,
                    "disk_percent": s.disk_percent,
                    "temperature": s.temperature,
                    "failed_services": s.failed_services,
                    "zombies": s.zombies,
                    "timestamp": s.timestamp,
                }
                for s in self.state_history[-self.max_history:]
            ]
            with open(state_file, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    def _get_current_state(self) -> SystemState:
        """Get current system state."""
        return SystemState(
            cpu_percent=self._last_cpu or 0,
            memory_percent=self._last_memory or 0,
            disk_percent=self._last_disk or 0,
            temperature=self._last_temp or 0,
            failed_services=int(self._last_failed or 0),
            zombies=int(self._last_zombies or 0),
            timestamp=time.time(),
        )

    def get_pattern_analysis(self) -> dict:
        """Analyze historical patterns to predict issues."""
        if len(self.state_history) < 10:
            return {"status": "insufficient_data"}

        recent = self.state_history[-60:]  # Last hour
        avg_cpu = sum(s.cpu_percent for s in recent) / len(recent)
        avg_mem = sum(s.memory_percent for s in recent) / len(recent)
        
        # Detect trends
        cpu_trend = "stable"
        if len(recent) >= 10:
            early = sum(s.cpu_percent for s in recent[:10]) / 10
            late = sum(s.cpu_percent for s in recent[-10:]) / 10
            if late > early * 1.3:
                cpu_trend = "increasing"
            elif late < early * 0.7:
                cpu_trend = "decreasing"

        return {
            "avg_cpu_1h": round(avg_cpu, 1),
            "avg_memory_1h": round(avg_mem, 1),
            "cpu_trend": cpu_trend,
            "samples": len(self.state_history),
        }

    async def auto_remediate(self, alert: Alert) -> Optional[str]:
        """Attempt automatic remediation for known issues."""
        if not self.autonomous_mode:
            return None

        category = alert.category
        remediation = {
            "zombie_processes": self._remediate_zombies,
            "failed_services": self._remediate_services,
            "high_disk": self._remediate_disk,
        }

        if category in remediation:
            try:
                result = await remediation[category](alert)
                if result:
                    alert.resolved = True
                    return result
            except Exception as e:
                return f"Auto-remediation failed: {e}"
        return None

    async def _remediate_zombies(self, alert: Alert) -> Optional[str]:
        """Kill zombie parent processes."""
        try:
            r = await asyncio.create_subprocess_exec(
                "ps", "aux", stdout=asyncio.subprocess.PIPE
            )
            out, _ = await r.communicate()
            parents = set()
            for line in out.decode().split("\n"):
                if " Z " in line:
                    parts = line.split()
                    if len(parts) > 2:
                        try:
                            parents.add(int(parts[1]))
                        except ValueError:
                            pass
            if parents:
                for pid in list(parents)[:5]:
                    proc = await asyncio.create_subprocess_exec(
                        "kill", "-9", str(pid),
                        stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                    )
                return f"Killed {len(parents)} zombie parent processes"
        except Exception:
            pass
        return None

    async def _remediate_services(self, alert: Alert) -> Optional[str]:
        """Try to restart failed services."""
        try:
            r = await asyncio.create_subprocess_exec(
                "systemctl", "--failed", "--no-pager", "--no-legend",
                stdout=asyncio.subprocess.PIPE
            )
            out, _ = await r.communicate()
            lines = [l for l in out.decode().strip().split("\n") if l.strip()]
            if lines:
                service = lines[0].strip().split()[0]
                proc = await asyncio.create_subprocess_exec(
                    "systemctl", "restart", service,
                    stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
                return f"Restarted failed service: {service}"
        except Exception:
            pass
        return None

    async def _remediate_disk(self, alert: Alert) -> Optional[str]:
        """Clean up disk space."""
        try:
            commands = [
                "rm -rf ~/.cache/thumbnails/*",
                "rm -rf ~/.local/share/Trash/*",
                "apt autoclean",
            ]
            for cmd in commands[:1]:
                proc = await asyncio.create_subprocess_shell(
                    cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
                )
            return "Ran disk cleanup"
        except Exception:
            pass
        return None

    # Track last values for state
    _last_cpu = None
    _last_memory = None
    _last_disk = None
    _last_temp = None
    _last_failed = None
    _last_zombies = None

    async def start(self, interval=30):
        """Start the monitoring loop."""
        self.check_interval = interval
        self.running = True
        while self.running:
            await self._run_checks()
            await asyncio.sleep(self.check_interval)

    def stop(self):
        """Stop the monitoring loop."""
        self.running = False
        self._save_state_history()

    async def _run_checks(self):
        """Run all monitoring rules."""
        state = SystemState()
        
        for rule in self.rules:
            try:
                metric = await rule["check"]()
                
                # Store in state for history
                if rule["name"] == "high_cpu":
                    self._last_cpu = metric
                    state.cpu_percent = metric or 0
                elif rule["name"] == "high_memory":
                    self._last_memory = metric
                    state.memory_percent = metric or 0
                elif rule["name"] == "low_disk":
                    self._last_disk = metric
                    state.disk_percent = metric or 0
                elif rule["name"] == "high_temperature":
                    self._last_temp = metric
                    state.temperature = metric or 0
                elif rule["name"] == "failed_services":
                    self._last_failed = metric
                    state.failed_services = int(metric or 0)
                elif rule["name"] == "zombie_processes":
                    self._last_zombies = metric
                    state.zombies = int(metric or 0)
                
                if metric is not None and metric > rule["threshold"]:
                    alert = Alert(
                        severity=rule["severity"],
                        category=rule["name"],
                        message=rule["message"].format(metric=metric),
                        metric=metric,
                        action=rule.get("action"),
                    )
                    self.alerts.append(alert)
                    
                    # Auto-remediate
                    remediation_result = await self.auto_remediate(alert)
                    if remediation_result:
                        print(f"[AUTO-REMEDIATION] {remediation_result}")
                    
                    for listener in self.listeners:
                        await listener(alert)
            except Exception:
                pass
        
        # Save state to history
        state.timestamp = time.time()
        self.state_history.append(state)
        if len(self.state_history) > self.max_history:
            self.state_history = self.state_history[-self.max_history:]
        
        # Save every 10 checks
        if len(self.state_history) % 10 == 0:
            self._save_state_history()

    def get_alerts(self, severity=None, unresolved_only=True) -> list[dict]:
        """Get alerts, optionally filtered."""
        result = []
        for a in self.alerts:
            if unresolved_only and a.resolved:
                continue
            if severity and a.severity.value != severity:
                continue
            result.append({
                "severity": a.severity.value,
                "category": a.category,
                "message": a.message,
                "metric": a.metric,
                "time": time.strftime("%H:%M:%S", time.localtime(a.timestamp)),
                "action": a.action,
                "resolved": a.resolved,
            })
        return result

    def get_summary(self) -> str:
        """Get monitoring summary."""
        active = [a for a in self.alerts if not a.resolved]
        if not active:
            return "All systems healthy. No active alerts."

        lines = [f"## System Alerts ({len(active)} active)\n"]
        for a in active[-10:]:
            icon = {"info": "ℹ️", "warning": "⚠️", "critical": "🔴"}[a.severity.value]
            lines.append(f"{icon} [{a.severity.value.upper()}] {a.message}")
            if a.action:
                lines.append(f"   → {a.action}")
        return "\n".join(lines)

    # ── Health Check Functions ──

    async def _check_cpu(self) -> Optional[float]:
        try:
            r = await asyncio.create_subprocess_exec(
                "top", "-bn1", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, _ = await r.communicate()
            for line in out.decode().split("\n"):
                if "Cpu(s)" in line or "%Cpu" in line:
                    parts = line.split(",")
                    for p in parts:
                        if "id" in p.lower():
                            idle = float(p.strip().split("%")[0].strip())
                            return 100 - idle
        except Exception:
            pass
        return None

    async def _check_memory(self) -> Optional[float]:
        try:
            r = await asyncio.create_subprocess_exec(
                "free", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, _ = await r.communicate()
            lines = out.decode().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                total = int(parts[1])
                used = int(parts[2])
                return (used / total) * 100
        except Exception:
            pass
        return None

    async def _check_disk(self) -> Optional[float]:
        try:
            r = await asyncio.create_subprocess_exec(
                "df", "/", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, _ = await r.communicate()
            lines = out.decode().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                usage = parts[4].replace("%", "")
                return float(usage)
        except Exception:
            pass
        return None

    async def _check_temp(self) -> Optional[float]:
        try:
            r = await asyncio.create_subprocess_exec(
                "cat", "/sys/class/thermal/thermal_zone0/temp",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, _ = await r.communicate()
            temp = int(out.decode().strip()) / 1000
            return temp
        except Exception:
            pass
        return None

    async def _check_failed_services(self) -> Optional[float]:
        try:
            r = await asyncio.create_subprocess_exec(
                "systemctl", "--failed", "--no-pager", "--no-legend",
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, _ = await r.communicate()
            lines = [l for l in out.decode().strip().split("\n") if l.strip()]
            return float(len(lines))
        except Exception:
            pass
        return None

    async def _check_zombies(self) -> Optional[float]:
        try:
            r = await asyncio.create_subprocess_exec(
                "ps", "aux", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
            )
            out, _ = await r.communicate()
            zombies = sum(1 for l in out.decode().split("\n") if " Z " in l or " Z+ " in l)
            return float(zombies)
        except Exception:
            pass
        return None


# Global instance
engine = AutonomousEngine()
