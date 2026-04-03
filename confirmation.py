"""Confirmation System - Approval for risky/dangerous actions.

Classifies actions by risk level and requires confirmation for dangerous ones.
"""
import asyncio
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class RiskLevel(Enum):
    SAFE = "safe"           # Read-only, no side effects
    LOW = "low"             # Minor changes, reversible
    MEDIUM = "medium"       # System changes, reversible
    HIGH = "high"           # System changes, hard to reverse
    CRITICAL = "critical"   # Destructive, irreversible


# Keyword-based risk classification
RISK_PATTERNS = {
    RiskLevel.CRITICAL: [
        "rm -rf", "mkfs", "dd if=", "format", "shred",
        "shutdown", "reboot", "halt", "poweroff",
        "userdel", "drop database", "drop table",
        "fdisk", "parted", "wipefs",
    ],
    RiskLevel.HIGH: [
        "rm ", "mv ", "kill ", "pkill", "killall",
        "iptables", "nftables", "ufw disable",
        "systemctl stop", "systemctl disable",
        "chmod 777", "chown", "passwd",
        "modprobe -r", "rmmod",
    ],
    RiskLevel.MEDIUM: [
        "systemctl start", "systemctl restart", "systemctl enable",
        "apt install", "apt remove", "pip install", "pip uninstall",
        "mount", "umount",
        "docker stop", "docker rm",
        "crontab", "git push",
    ],
    RiskLevel.LOW: [
        "mkdir", "touch", "cp ", "cp -r",
        "echo >", "tee ",
        "docker start", "docker pull",
    ],
}


@dataclass
class PendingAction:
    action_id: str
    command: str
    risk_level: RiskLevel
    reason: str
    timestamp: float = field(default_factory=time.time)
    approved: bool = False
    rejected: bool = False
    result: Optional[str] = None


class ConfirmationSystem:
    """Manages approval for risky actions."""

    def __init__(self):
        self.pending: dict[str, PendingAction] = {}
        self.history: list[PendingAction] = []
        self.auto_approve_safe = True
        self.auto_approve_low = False
        self._id_counter = 0

    def classify(self, command: str) -> tuple[RiskLevel, str]:
        """Classify a command by risk level."""
        cmd_lower = command.lower().strip()

        for level in [RiskLevel.CRITICAL, RiskLevel.HIGH, RiskLevel.MEDIUM, RiskLevel.LOW]:
            for pattern in RISK_PATTERNS[level]:
                if pattern in cmd_lower:
                    return level, f"Matched pattern: {pattern}"

        return RiskLevel.SAFE, "No risky patterns detected"

    def request_approval(self, command: str) -> dict:
        """Request approval for a command. Returns action details."""
        risk_level, reason = self.classify(command)

        # Auto-approve safe commands
        if risk_level == RiskLevel.SAFE and self.auto_approve_safe:
            return {"approved": True, "risk_level": "safe", "reason": "Auto-approved (safe)"}

        if risk_level == RiskLevel.LOW and self.auto_approve_low:
            return {"approved": True, "risk_level": "low", "reason": "Auto-approved (low risk)"}

        # Create pending action
        self._id_counter += 1
        action_id = f"action_{self._id_counter}_{int(time.time())}"
        action = PendingAction(
            action_id=action_id,
            command=command,
            risk_level=risk_level,
            reason=reason,
        )
        self.pending[action_id] = action

        return {
            "approved": False,
            "action_id": action_id,
            "risk_level": risk_level.value,
            "reason": reason,
            "message": f"⚠️ {risk_level.value.upper()} risk action requires approval:\n"
                       f"Command: {command}\nReason: {reason}\n"
                       f"Use approve('{action_id}') to proceed or reject('{action_id}') to cancel.",
        }

    def approve(self, action_id: str) -> dict:
        """Approve a pending action."""
        if action_id not in self.pending:
            return {"error": f"No pending action: {action_id}"}

        action = self.pending.pop(action_id)
        action.approved = True
        self.history.append(action)
        return {"approved": True, "command": action.command, "risk_level": action.risk_level.value}

    def reject(self, action_id: str) -> dict:
        """Reject a pending action."""
        if action_id not in self.pending:
            return {"error": f"No pending action: {action_id}"}

        action = self.pending.pop(action_id)
        action.rejected = True
        self.history.append(action)
        return {"rejected": True, "command": action.command}

    def get_pending(self) -> list[dict]:
        """Get all pending approvals."""
        return [
            {
                "id": a.action_id,
                "command": a.command,
                "risk": a.risk_level.value,
                "reason": a.reason,
            }
            for a in self.pending.values()
        ]

    def get_history(self, limit=20) -> list[dict]:
        """Get approval history."""
        return [
            {
                "command": a.command,
                "risk": a.risk_level.value,
                "approved": a.approved,
                "time": time.strftime("%H:%M:%S", time.localtime(a.timestamp)),
            }
            for a in self.history[-limit:]
        ]


# Global instance
confirm = ConfirmationSystem()
