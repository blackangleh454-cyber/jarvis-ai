"""Intelligence Layer - The 5 missing pieces for human-level autonomy.

1. Think Tool       - Internal reasoning before actions
2. Skill Builder    - Auto-create new skills from scratch
3. Self-Modifier    - Rewrite own prompts based on experience
4. Loop Engine      - Multi-step reasoning loop
5. Gap Detector     - Detect repeated failures, auto-build solutions
"""
import os
import json
import time
import subprocess
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ═══════════════════════════════════════════════════════
# 1. THINK TOOL - Internal monologue before acting
# ═══════════════════════════════════════════════════════

@dataclass
class Thought:
    question: str
    reasoning: str
    plan: list
    risk_level: str
    confidence: float
    timestamp: float = field(default_factory=time.time)


class ThinkTool:
    """Internal reasoning engine. Think before you act."""

    def __init__(self):
        self.thought_log: list[Thought] = []

    def think(self, situation: str, context: str = "") -> dict:
        """Structured thinking process.

        Returns a decision framework the LLM can use.
        """
        thought = {
            "situation": situation,
            "context": context[:500] if context else "",
            "timestamp": time.strftime("%H:%M:%S"),
            "framework": {
                "1_understand": "What is the user actually asking?",
                "2_assess": "What tools/skills do I have for this?",
                "3_plan": "What's the step-by-step plan?",
                "4_risks": "What could go wrong?",
                "5_verify": "How will I know it worked?",
            },
            "decision": {
                "should_act": True,
                "needs_approval": False,
                "estimated_steps": 1,
                "fallback_plan": "If this fails, explain the issue and suggest alternatives.",
            },
        }

        # Auto-detect risk patterns
        risky_patterns = ["delete", "remove", "kill", "format", "shutdown", "reboot"]
        if any(p in situation.lower() for p in risky_patterns):
            thought["decision"]["needs_approval"] = True
            thought["decision"]["risk_level"] = "high"

        return thought

    def plan(self, goal: str, available_tools: list = None) -> list:
        """Generate a step-by-step plan for a goal."""
        return [
            {"step": 1, "action": "Understand the request fully"},
            {"step": 2, "action": "Check available tools and skills"},
            {"step": 3, "action": "Execute the primary action"},
            {"step": 4, "action": "Verify the result"},
            {"step": 5, "action": "Report back to user"},
        ]

    def reflect(self, action: str, result: str, expected: str = "") -> dict:
        """Reflect on an action's outcome. Learn from it."""
        success = "error" not in result.lower() and "fail" not in result.lower()

        reflection = {
            "action": action,
            "result_preview": result[:200],
            "success": success,
            "analysis": "Worked as expected." if success else "Something went wrong. Need to analyze.",
            "learning": None,
            "next_action": None,
        }

        if not success:
            reflection["next_action"] = "Try alternative approach or ask user for guidance"
            reflection["learning"] = f"Action '{action}' failed with: {result[:100]}"

        return reflection

    def get_thought_log(self, limit=10) -> str:
        """Get recent thinking history."""
        if not self.thought_log:
            return "No thoughts logged yet."
        lines = []
        for t in self.thought_log[-limit:]:
            lines.append(f"[{time.strftime('%H:%M:%S', time.localtime(t.timestamp))}] {t.question}")
            lines.append(f"  Plan: {t.plan}")
            lines.append(f"  Risk: {t.risk_level} | Confidence: {t.confidence}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# 2. SKILL BUILDER - Auto-create new skills
# ═══════════════════════════════════════════════════════

class SkillBuilder:
    """Build new skills from scratch. Write code, test, deploy."""

    def __init__(self, skills_dir: str = None):
        self.skills_dir = skills_dir or os.path.join(BASE_DIR, "skills")

    def create_skill(self, name: str, description: str,
                     commands: list, test_commands: bool = True) -> dict:
        """Create a complete new skill with handler.py + SKILL.md.

        Args:
            name: Skill name (lowercase, hyphens)
            description: What the skill does
            commands: List of {"name": "cmd_name", "desc": "...", "shell": "actual command"}
            test_commands: Whether to test commands before deploying
        """
        # Validate name
        name = re.sub(r'[^a-z0-9-]', '-', name.lower().strip())
        skill_dir = os.path.join(self.skills_dir, name)

        if os.path.exists(skill_dir):
            return {"error": f"Skill '{name}' already exists"}

        os.makedirs(skill_dir, exist_ok=True)

        # Generate handler.py
        handler_code = self._generate_handler(name, commands)
        handler_path = os.path.join(skill_dir, "handler.py")
        with open(handler_path, "w") as f:
            f.write(handler_code)
        os.chmod(handler_path, 0o755)

        # Generate SKILL.md
        skill_md = self._generate_skill_md(name, description, commands)
        with open(os.path.join(skill_dir, "SKILL.md"), "w") as f:
            f.write(skill_md)

        # Test if requested
        test_results = []
        if test_commands:
            for cmd in commands[:3]:  # Test first 3
                try:
                    r = subprocess.run(
                        cmd.get("shell", "echo ok"),
                        shell=True, capture_output=True, text=True, timeout=10
                    )
                    test_results.append({
                        "command": cmd["name"],
                        "status": "pass" if r.returncode == 0 else "fail",
                        "output": (r.stdout or r.stderr)[:100],
                    })
                except Exception as e:
                    test_results.append({
                        "command": cmd["name"],
                        "status": "error",
                        "output": str(e)[:100],
                    })

        return {
            "success": True,
            "name": name,
            "path": skill_dir,
            "files": ["handler.py", "SKILL.md"],
            "tests": test_results,
            "message": f"Skill '{name}' created. Restart JARVIS or it will auto-discover on next load.",
        }

    def _generate_handler(self, name: str, commands: list) -> str:
        """Generate handler.py code."""
        lines = [
            '#!/usr/bin/env python3',
            f'"""Auto-generated skill: {name}"""',
            'import sys, subprocess',
            'SUDO = "echo \'ok\' | sudo -S"',
            'def run(cmd):',
            '    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)',
            '    return r.stdout.strip() if r.returncode == 0 else f"Error: {r.stderr.strip()}"',
            '',
        ]

        for cmd in commands:
            func_name = re.sub(r'[^a-z0-9_]', '_', cmd["name"].lower())
            shell_cmd = cmd.get("shell", "echo ok")
            lines.append(f'def {func_name}():')
            lines.append(f'    return run("{shell_cmd}")')
            lines.append('')

        lines.append('if __name__ == "__main__":')
        lines.append('    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"')
        for cmd in commands:
            func_name = re.sub(r'[^a-z0-9_]', '_', cmd["name"].lower())
            lines.append(f'    if cmd == "{cmd["name"]}": print({func_name}())')
        lines.append(f'    else: print("Commands: {", ".join(c["name"] for c in commands)}")')

        return "\n".join(lines)

    def _generate_skill_md(self, name: str, description: str, commands: list) -> str:
        """Generate SKILL.md content."""
        lines = [
            '---',
            f'name: {name}',
            f'description: "{description}"',
            '---',
            '',
            f'# {name.replace("-", " ").title()}',
            '',
            description,
            '',
            '## Commands',
            '',
        ]
        for cmd in commands:
            lines.append(f'- `{cmd["name"]}` — {cmd.get("desc", "No description")}')

        return "\n".join(lines)

    def enhance_skill(self, skill_name: str, new_commands: list) -> dict:
        """Add new commands to an existing skill."""
        skill_dir = os.path.join(self.skills_dir, skill_name)
        if not os.path.exists(skill_dir):
            return {"error": f"Skill '{skill_name}' not found"}

        handler_path = os.path.join(skill_dir, "handler.py")
        with open(handler_path, "r") as f:
            content = f.read()

        # Append new functions
        new_code = "\n\n# Auto-added functions\n"
        for cmd in new_commands:
            func_name = re.sub(r'[^a-z0-9_]', '_', cmd["name"].lower())
            shell_cmd = cmd.get("shell", "echo ok")
            new_code += f'def {func_name}():\n    return run("{shell_cmd}")\n\n'

        # Insert before the if __name__ block
        if 'if __name__' in content:
            parts = content.split('if __name__')
            content = parts[0] + new_code + '\nif __name__' + parts[1]
        else:
            content += new_code

        with open(handler_path, "w") as f:
            f.write(content)

        return {"success": True, "message": f"Added {len(new_commands)} commands to {skill_name}"}

    def fix_skill(self, skill_name: str, error: str, fix_code: str) -> dict:
        """Fix a broken skill based on error message."""
        skill_dir = os.path.join(self.skills_dir, skill_name)
        if not os.path.exists(skill_dir):
            return {"error": f"Skill '{skill_name}' not found"}

        handler_path = os.path.join(skill_dir, "handler.py")
        with open(handler_path, "r") as f:
            content = f.read()

        # Save backup
        with open(handler_path + ".bak", "w") as f:
            f.write(content)

        # Apply fix (the LLM provides the fixed code)
        with open(handler_path, "w") as f:
            f.write(fix_code)

        return {"success": True, "message": f"Fixed {skill_name}. Backup saved as handler.py.bak"}


# ═══════════════════════════════════════════════════════
# 3. SELF-MODIFIER - Rewrite own prompts
# ═══════════════════════════════════════════════════════

class SelfModifier:
    """Modify JARVIS's own prompts and behavior based on experience."""

    def __init__(self, prompts_file: str = None):
        self.prompts_file = prompts_file or os.path.join(BASE_DIR, "jarvis_prompts.py")
        self.modifications_log = []

    def add_rule(self, rule: str, section: str = "INSTRUCTIONS") -> dict:
        """Add a new behavioral rule to the system prompts."""
        try:
            with open(self.prompts_file, "r") as f:
                content = f.read()

            # Find the section and append the rule
            marker = f'{section} = """'
            if marker in content:
                idx = content.index(marker) + len(marker)
                # Find the closing """
                end = content.index('"""', idx)
                # Insert rule before closing
                new_content = content[:end] + f"\n- {rule}\n" + content[end:]

                with open(self.prompts_file, "w") as f:
                    f.write(new_content)

                self.modifications_log.append({
                    "type": "add_rule",
                    "section": section,
                    "rule": rule,
                    "time": time.strftime("%H:%M:%S"),
                })

                return {"success": True, "message": f"Added rule to {section}: {rule}"}
            else:
                return {"error": f"Section {section} not found"}

        except Exception as e:
            return {"error": str(e)}

    def update_identity(self, trait: str) -> dict:
        """Add a personality trait to JARVIS's identity."""
        return self.add_rule(trait, "IDENTITY")

    def record_correction(self, what_was_wrong: str, what_is_correct: str) -> dict:
        """Record a user correction for future reference."""
        rule = f"Previously: {what_was_wrong}. Correct: {what_is_correct}"
        return self.add_rule(rule, "INSTRUCTIONS")

    def get_modifications(self) -> str:
        """Get history of self-modifications."""
        if not self.modifications_log:
            return "No self-modifications yet."
        lines = []
        for m in self.modifications_log[-10:]:
            lines.append(f"[{m['time']}] {m['type']}: {m.get('rule', 'N/A')}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════
# 4. LOOP ENGINE - Multi-step reasoning
# ═══════════════════════════════════════════════════════

@dataclass
class LoopStep:
    step_num: int
    action: str
    tool_used: str
    result: str
    success: bool
    timestamp: float = field(default_factory=time.time)


class LoopEngine:
    """Multi-step reasoning: act → observe → decide → loop."""

    def __init__(self):
        self.active_loops: dict[str, list[LoopStep]] = {}
        self._id_counter = 0

    def start_loop(self, goal: str) -> str:
        """Start a new reasoning loop."""
        self._id_counter += 1
        loop_id = f"loop_{self._id_counter}_{int(time.time())}"
        self.active_loops[loop_id] = []
        return loop_id

    def add_step(self, loop_id: str, action: str, tool: str, result: str, success: bool):
        """Record a step in the loop."""
        if loop_id not in self.active_loops:
            return
        steps = self.active_loops[loop_id]
        step = LoopStep(
            step_num=len(steps) + 1,
            action=action,
            tool_used=tool,
            result=result[:500],
            success=success,
        )
        steps.append(step)

    def should_continue(self, loop_id: str, max_steps: int = 10) -> dict:
        """Decide whether to continue the loop or stop."""
        steps = self.active_loops.get(loop_id, [])
        last_step = steps[-1] if steps else None

        if len(steps) >= max_steps:
            return {"continue": False, "reason": "Max steps reached"}

        if last_step and last_step.success:
            return {"continue": False, "reason": "Goal achieved"}

        # Check for repeated failures
        if len(steps) >= 3:
            last_3 = steps[-3:]
            if all(not s.success for s in last_3):
                return {"continue": False, "reason": "3 consecutive failures. Try different approach."}

        return {"continue": True, "reason": "Ready for next step"}

    def get_loop_history(self, loop_id: str) -> str:
        """Get human-readable loop history."""
        steps = self.active_loops.get(loop_id, [])
        if not steps:
            return f"Loop {loop_id} not found"

        lines = [f"## Loop: {loop_id} ({len(steps)} steps)\n"]
        for s in steps:
            icon = "✅" if s.success else "❌"
            lines.append(f"  Step {s.step_num}: {icon} {s.action}")
            lines.append(f"    Tool: {s.tool_used} | Result: {s.result[:100]}")
        return "\n".join(lines)

    def get_summary(self, loop_id: str) -> dict:
        """Summarize a completed loop."""
        steps = self.active_loops.get(loop_id, [])
        successful = sum(1 for s in steps if s.success)
        failed = sum(1 for s in steps if not s.success)
        return {
            "total_steps": len(steps),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful/len(steps)*100):.0f}%" if steps else "0%",
            "tools_used": list(set(s.tool_used for s in steps)),
        }


# ═══════════════════════════════════════════════════════
# 5. GAP DETECTOR - Detect failures, auto-build solutions
# ═══════════════════════════════════════════════════════

@dataclass
class Gap:
    pattern: str
    occurrences: int
    first_seen: float
    last_seen: float
    examples: list = field(default_factory=list)
    resolved: bool = False
    solution: Optional[str] = None


class GapDetector:
    """Detect repeated failures and capability gaps. Auto-suggest solutions."""

    def __init__(self):
        self.gaps: dict[str, Gap] = {}
        self.failure_history: list[dict] = []

    def record_failure(self, action: str, error: str, context: str = ""):
        """Record a failed action for pattern detection."""
        self.failure_history.append({
            "action": action,
            "error": error[:200],
            "context": context[:200],
            "time": time.time(),
        })

        # Normalize the failure pattern
        pattern = self._normalize_pattern(action, error)

        if pattern in self.gaps:
            gap = self.gaps[pattern]
            gap.occurrences += 1
            gap.last_seen = time.time()
            if len(gap.examples) < 5:
                gap.examples.append(f"{action}: {error[:100]}")
        else:
            self.gaps[pattern] = Gap(
                pattern=pattern,
                occurrences=1,
                first_seen=time.time(),
                last_seen=time.time(),
                examples=[f"{action}: {error[:100]}"],
            )

    def _normalize_pattern(self, action: str, error: str) -> str:
        """Normalize a failure into a detectable pattern."""
        # Extract the core issue
        if "command not found" in error.lower() or "no such file" in error.lower():
            cmd = action.split()[0] if action else "unknown"
            return f"missing_tool:{cmd}"
        elif "permission denied" in error.lower():
            return f"permission:{action[:30]}"
        elif "connection refused" in error.lower() or "timeout" in error.lower():
            return f"network:{action[:30]}"
        elif "no module named" in error.lower():
            return f"missing_module:{action[:30]}"
        else:
            return f"error:{action[:30]}"

    def detect_gaps(self) -> list[dict]:
        """Find recurring patterns (gaps that need solutions)."""
        recurring = []
        for pattern, gap in self.gaps.items():
            if gap.occurrences >= 2 and not gap.resolved:
                recurring.append({
                    "pattern": pattern,
                    "occurrences": gap.occurrences,
                    "examples": gap.examples[:3],
                    "suggestion": self._suggest_solution(pattern),
                })
        return sorted(recurring, key=lambda x: x["occurrences"], reverse=True)

    def _suggest_solution(self, pattern: str) -> str:
        """Suggest a solution based on the gap pattern."""
        if pattern.startswith("missing_tool:"):
            tool = pattern.split(":")[1]
            return f"Install: sudo apt-get install -y {tool}"
        elif pattern.startswith("permission:"):
            return "Run with sudo or check file permissions"
        elif pattern.startswith("network:"):
            return "Check network connectivity, firewall, or service status"
        elif pattern.startswith("missing_module:"):
            mod = pattern.split(":")[1]
            return f"Install: pip install {mod}"
        return "Investigate the error and implement a fix"

    def get_report(self) -> str:
        """Generate a gap analysis report."""
        gaps = self.detect_gaps()
        if not gaps:
            return "No recurring gaps detected. All systems operational."

        lines = [f"## Gap Analysis ({len(gaps)} recurring issues)\n"]
        for g in gaps:
            lines.append(f"**Pattern**: {g['pattern']}")
            lines.append(f"**Occurrences**: {g['occurrences']}")
            lines.append(f"**Suggestion**: {g['suggestion']}")
            lines.append(f"**Examples**: {g['examples'][0] if g['examples'] else 'N/A'}")
            lines.append("")
        return "\n".join(lines)

    def mark_resolved(self, pattern: str, solution: str):
        """Mark a gap as resolved."""
        if pattern in self.gaps:
            self.gaps[pattern].resolved = True
            self.gaps[pattern].solution = solution


# ═══════════════════════════════════════════════════════
# GLOBAL INSTANCES
# ═══════════════════════════════════════════════════════

think_tool = ThinkTool()
skill_builder = SkillBuilder()
self_modifier = SelfModifier()
loop_engine = LoopEngine()
gap_detector = GapDetector()
