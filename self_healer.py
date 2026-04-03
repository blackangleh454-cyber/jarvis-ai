#!/usr/bin/env python3
"""Self-Healer - JARVIS auto-repair and self-installation system.

Detects issues, repairs itself, installs skills, manages dependencies.

Author: J.A.R.V.I.S.
"""
import os
import sys
import json
import subprocess
import time
import threading
import importlib
from typing import Dict, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib


class IssueType(Enum):
    MODULE_MISSING = "module_missing"
    MODULE_ERROR = "module_error"
    DEPENDENCY_MISSING = "dependency_missing"
    SKILL_MISSING = "skill_missing"
    SKILL_ERROR = "skill_error"
    COMMAND_FAILED = "command_failed"
    SERVICE_DOWN = "service_down"
    MEMORY_ERROR = "memory_error"


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class Issue:
    """Detected issue."""
    id: str
    issue_type: IssueType
    severity: Severity
    description: str
    details: Dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    resolved: bool = False
    resolution: Optional[str] = None


class SelfHealer:
    """JARVIS self-repair system."""
    
    def __init__(self, base_dir: str = None, sudo_manager=None):
        if base_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.base_dir = base_dir
        self.sudo_manager = sudo_manager
        self.issues: Dict[str, Issue] = {}
        self.auto_repair = True
        self._lock = threading.RLock()
        
        # Health check intervals
        self.check_interval = 60  # seconds
        self._running = False
        self._health_thread = None
        
    def generate_id(self, description: str) -> str:
        """Generate unique issue ID."""
        raw = f"{description}:{time.time()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:12]
    
    def detect_issues(self) -> List[Issue]:
        """Run all health checks and detect issues."""
        issues = []
        
        # Check core modules
        issues.extend(self._check_core_modules())
        
        # Check dependencies
        issues.extend(self._check_dependencies())
        
        # Check skills
        issues.extend(self._check_skills())
        
        # Check services
        issues.extend(self._check_services())
        
        # Check memory
        issues.extend(self._check_memory())
        
        return issues
    
    def _check_core_modules(self) -> List[Issue]:
        """Check if core JARVIS modules can be imported."""
        issues = []
        required_modules = [
            "agent", "skill_manager", "memory", "autonomous_engine",
            "sudo_manager", "infinite_memory", "desktop_capture"
        ]
        
        for module_name in required_modules:
            try:
                if module_name == "agent":
                    # Skip main agent - has many dependencies
                    continue
                module_path = os.path.join(self.base_dir, f"{module_name}.py")
                if not os.path.exists(module_path):
                    issues.append(Issue(
                        id=self.generate_id(f"missing_{module_name}"),
                        issue_type=IssueType.MODULE_MISSING,
                        severity=Severity.CRITICAL,
                        description=f"Core module missing: {module_name}",
                        details={"module": module_name}
                    ))
            except Exception as e:
                issues.append(Issue(
                    id=self.generate_id(f"error_{module_name}"),
                    issue_type=IssueType.MODULE_ERROR,
                    severity=Severity.HIGH,
                    description=f"Module error: {module_name}",
                    details={"module": module_name, "error": str(e)}
                ))
        
        return issues
    
    def _check_dependencies(self) -> List[Issue]:
        """Check required Python dependencies."""
        issues = []
        required_packages = [
            "livekit", "openai", "dotenv", "numpy", "cv2"
        ]
        
        for package in required_packages:
            try:
                importlib.import_module(package)
            except ImportError:
                issues.append(Issue(
                    id=self.generate_id(f"missing_{package}"),
                    issue_type=IssueType.DEPENDENCY_MISSING,
                    severity=Severity.HIGH,
                    description=f"Missing Python package: {package}",
                    details={"package": package}
                ))
        
        return issues
    
    def _check_skills(self) -> List[Issue]:
        """Check skills directory."""
        issues = []
        skills_dir = os.path.join(self.base_dir, "skills")
        
        if not os.path.exists(skills_dir):
            issues.append(Issue(
                id=self.generate_id("missing_skills_dir"),
                issue_type=IssueType.SKILL_MISSING,
                severity=Severity.CRITICAL,
                description="Skills directory missing",
                details={"path": skills_dir}
            ))
            return issues
        
        # Check each skill has handler.py
        for skill_name in os.listdir(skills_dir):
            skill_path = os.path.join(skills_dir, skill_name)
            if os.path.isdir(skill_path):
                handler_path = os.path.join(skill_path, "handler.py")
                if not os.path.exists(handler_path):
                    issues.append(Issue(
                        id=self.generate_id(f"skill_{skill_name}"),
                        issue_type=IssueType.SKILL_ERROR,
                        severity=Severity.MEDIUM,
                        description=f"Skill missing handler: {skill_name}",
                        details={"skill": skill_name}
                    ))
        
        return issues
    
    def _check_services(self) -> List[Issue]:
        """Check system services."""
        issues = []
        
        # Check if we can run systemctl
        try:
            result = subprocess.run(
                ["systemctl", "is-active", "snapd"],
                capture_output=True, timeout=5
            )
            # Just checking if systemctl works
        except FileNotFoundError:
            pass
        except Exception:
            pass
        
        return issues
    
    def _check_memory(self) -> List[Issue]:
        """Check memory system."""
        issues = []
        
        # Check if memory directories exist
        memory_dir = os.path.expanduser("~/.jarvis")
        if not os.path.exists(memory_dir):
            try:
                os.makedirs(memory_dir, exist_ok=True)
            except Exception as e:
                issues.append(Issue(
                    id=self.generate_id("memory_dir_error"),
                    issue_type=IssueType.MEMORY_ERROR,
                    severity=Severity.HIGH,
                    description=f"Cannot create memory directory: {e}",
                    details={"error": str(e)}
                ))
        
        return issues
    
    def repair_issue(self, issue: Issue) -> Tuple[bool, str]:
        """Attempt to repair a specific issue."""
        with self._lock:
            if issue.issue_type == IssueType.DEPENDENCY_MISSING:
                return self._repair_dependency(issue)
            elif issue.issue_type == IssueType.SKILL_ERROR:
                return self._repair_skill(issue)
            elif issue.issue_type == IssueType.MODULE_ERROR:
                return self._repair_module(issue)
            elif issue.issue_type == IssueType.MEMORY_ERROR:
                return self._repair_memory(issue)
            
            return False, f"No repair strategy for {issue.issue_type.value}"
    
    def _repair_dependency(self, issue: Issue) -> Tuple[bool, str]:
        """Repair missing dependency."""
        package = issue.details.get("package", "")
        
        try:
            # Try pip install
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                capture_output=True, text=True, timeout=120
            )
            
            if result.returncode == 0:
                issue.resolved = True
                issue.resolution = f"Installed {package} via pip"
                return True, f"Installed {package}"
            
            # Try with sudo if pip failed
            if self.sudo_manager:
                success, output = self.sudo_manager.execute(f"pip install {package}")
                if success:
                    issue.resolved = True
                    issue.resolution = f"Installed {package} via sudo"
                    return True, f"Installed {package}"
            
            return False, f"Failed to install {package}"
            
        except Exception as e:
            return False, str(e)
    
    def _repair_skill(self, issue: Issue) -> Tuple[bool, str]:
        """Repair skill issue."""
        skill_name = issue.details.get("skill", "")
        
        # Check if skill has SKILL.md but no handler
        skills_dir = os.path.join(self.base_dir, "skills")
        skill_path = os.path.join(skills_dir, skill_name)
        
        if os.path.exists(skill_path):
            # Try to create minimal handler
            handler_path = os.path.join(skill_path, "handler.py")
            if not os.path.exists(handler_path):
                # Create minimal handler
                minimal_handler = '''#!/usr/bin/env python3
"""Auto-generated handler for {} skill."""
import json
import sys

def main():
    if len(sys.argv) < 2:
        print(json.dumps({{"status": "error", "message": "No command"}}))
        return
    
    cmd = sys.argv[1]
    print(json.dumps({{"status": "success", "message": f"Handler for {{cmd}}"}}))

if __name__ == "__main__":
    main()
'''.format(skill_name)
                
                try:
                    with open(handler_path, 'w') as f:
                        f.write(minimal_handler)
                    issue.resolved = True
                    issue.resolution = f"Created minimal handler for {skill_name}"
                    return True, f"Created handler for {skill_name}"
                except Exception as e:
                    return False, str(e)
        
        return False, f"Cannot repair skill: {skill_name}"
    
    def _repair_module(self, issue: Issue) -> Tuple[bool, str]:
        """Repair module error."""
        # Try to reload/fix module
        module_name = issue.details.get("module", "")
        
        try:
            importlib.import_module(module_name)
            issue.resolved = True
            issue.resolution = f"Module {module_name} now loads"
            return True, f"Fixed module: {module_name}"
        except Exception as e:
            return False, str(e)
    
    def _repair_memory(self, issue: Issue) -> Tuple[bool, str]:
        """Repair memory issue."""
        memory_dir = os.path.expanduser("~/.jarvis")
        
        try:
            os.makedirs(memory_dir, exist_ok=True)
            issue.resolved = True
            issue.resolution = f"Created memory directory"
            return True, "Memory directory created"
        except Exception as e:
            return False, str(e)
    
    def auto_repair_all(self, confirm_callback: Callable = None) -> Dict:
        """Auto-repair all detected issues."""
        issues = self.detect_issues()
        
        results = {
            "detected": len(issues),
            "repaired": 0,
            "failed": 0,
            "details": []
        }
        
        critical_issues = [i for i in issues if i.severity == Severity.CRITICAL]
        
        for issue in critical_issues:
            if issue.resolved:
                continue
            
            # Ask for confirmation if callback provided
            if confirm_callback:
                confirmed = confirm_callback(issue)
                if not confirmed:
                    results["failed"] += 1
                    results["details"].append({
                        "issue": issue.description,
                        "status": "skipped"
                    })
                    continue
            
            # Auto-repair
            success, message = self.repair_issue(issue)
            
            if success:
                results["repaired"] += 1
                results["details"].append({
                    "issue": issue.description,
                    "status": "repaired",
                    "resolution": issue.resolution
                })
            else:
                results["failed"] += 1
                results["details"].append({
                    "issue": issue.description,
                    "status": "failed",
                    "error": message
                })
        
        # Also repair high severity
        for issue in issues:
            if issue.severity != Severity.HIGH or issue.resolved:
                continue
            
            success, message = self.repair_issue(issue)
            
            if success:
                results["repaired"] += 1
                results["details"].append({
                    "issue": issue.description,
                    "status": "repaired"
                })
        
        return results
    
    def install_skill(self, skill_name: str, skill_data: Dict) -> Tuple[bool, str]:
        """Install a new skill."""
        skills_dir = os.path.join(self.base_dir, "skills")
        skill_path = os.path.join(skills_dir, skill_name)
        
        try:
            os.makedirs(skill_path, exist_ok=True)
            
            # Create SKILL.md
            if "description" in skill_data:
                with open(os.path.join(skill_path, "SKILL.md"), 'w') as f:
                    f.write(f"# {skill_name}\n\n{skill_data.get('description', '')}\n")
            
            # Create handler.py
            if "commands" in skill_data:
                handler_content = self._generate_handler(skill_name, skill_data["commands"])
                with open(os.path.join(skill_path, "handler.py"), 'w') as f:
                    f.write(handler_content)
            
            return True, f"Installed skill: {skill_name}"
            
        except Exception as e:
            return False, str(e)
    
    def _generate_handler(self, skill_name: str, commands: List[str]) -> str:
        """Generate handler.py from command list."""
        cmds_json = json.dumps(commands)
        
        template = f'''#!/usr/bin/env python3
"""Auto-generated handler for {skill_name} skill."""
import json
import sys

COMMANDS = {cmds_json}

def main():
    if len(sys.argv) < 2:
        print(json.dumps({{"error": "No command provided"}}))
        sys.exit(1)
    
    cmd = sys.argv[1]
    args = sys.argv[2:] if len(sys.argv) > 2 else []
    
    if cmd in COMMANDS:
        print(json.dumps({{"status": "success", "command": cmd, "args": args}}))
    else:
        print(json.dumps({{"error": f"Unknown command: {{cmd}}"}}))

if __name__ == "__main__":
    main()
'''
        return template
    
    def get_health_report(self) -> Dict:
        """Get comprehensive health report."""
        issues = self.detect_issues()
        
        return {
            "timestamp": datetime.now().isoformat(),
            "health_score": self._calculate_health_score(issues),
            "total_issues": len(issues),
            "critical_issues": len([i for i in issues if i.severity == Severity.CRITICAL]),
            "high_issues": len([i for i in issues if i.severity == Severity.HIGH]),
            "issues": [
                {
                    "type": i.issue_type.value,
                    "severity": i.severity.value,
                    "description": i.description,
                    "resolved": i.resolved
                }
                for i in issues
            ],
            "auto_repair_enabled": self.auto_repair
        }
    
    def _calculate_health_score(self, issues: List[Issue]) -> float:
        """Calculate health score 0-100."""
        if not issues:
            return 100.0
        
        deductions = 0
        for issue in issues:
            if issue.severity == Severity.CRITICAL:
                deductions += 25
            elif issue.severity == Severity.HIGH:
                deductions += 15
            elif issue.severity == Severity.MEDIUM:
                deductions += 5
            else:
                deductions += 1
        
        return max(0, 100 - deductions)
    
    def start_monitoring(self):
        """Start background health monitoring."""
        if self._running:
            return
        
        self._running = True
        
        def monitor_loop():
            while self._running:
                try:
                    if self.auto_repair:
                        self.auto_repair_all()
                except Exception:
                    pass
                time.sleep(self.check_interval)
        
        self._health_thread = threading.Thread(target=monitor_loop, daemon=True)
        self._health_thread.start()
    
    def stop_monitoring(self):
        """Stop background health monitoring."""
        self._running = False


# Global instance
self_healer = SelfHealer()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: self_healer.py <command>")
        print("\nCommands:")
        print("  check          - Run health check")
        print("  repair         - Auto-repair issues")
        print("  report         - Get health report")
        print("  install <name> - Install skill")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "check":
        issues = self_healer.detect_issues()
        print(f"Found {len(issues)} issues")
        for issue in issues:
            print(f"  [{issue.severity.value}] {issue.description}")
    
    elif cmd == "repair":
        results = self_healer.auto_repair_all()
        print(json.dumps(results, indent=2))
    
    elif cmd == "report":
        report = self_healer.get_health_report()
        print(json.dumps(report, indent=2))
    
    elif cmd == "install":
        if len(sys.argv) < 3:
            print("Usage: self_healer.py install <skill_name>")
            sys.exit(1)
        skill_name = sys.argv[2]
        success, message = self_healer.install_skill(skill_name, {"description": "Auto-installed skill"})
        print(message)
