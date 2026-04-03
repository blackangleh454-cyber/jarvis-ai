"""Reasoning Brain - GLM-5 powered deep thinking for JARVIS.

Uses Modal-hosted GLM-5-FP8 for:
- Chain-of-thought reasoning
- Multi-step planning
- Code/skill generation
- Error diagnosis
- Gap analysis and solutions

Gemini handles voice. GLM-5 handles thinking.
"""
import os
import json
import subprocess


class ReasoningBrain:
    """GLM-5 (Modal) powered reasoning engine."""

    def __init__(self):
        self.api_url = os.getenv(
            "GLM5_API_URL",
            "https://api.us-west-2.modal.direct/v1/chat/completions"
        )
        self.api_key = os.getenv(
            "GLM5_API_KEY",
            "modalresearch_hKhR3UZ4kn8ns6BrekpcnyyvobSfae_HHYmZcegTa_Y"
        )
        self.model = "zai-org/GLM-5-FP8"

        # Mercury-2 fallback
        self.fallback_url = "https://api.inceptionlabs.ai/v1/chat/completions"
        self.fallback_key = "sk_ae035f37e4571ebc168816782a9f0c9f"
        self.fallback_model = "mercury-2"

    def is_available(self) -> bool:
        return bool(self.api_key or self.fallback_key)

    def _call(self, system: str, user: str, max_tokens: int = 2000) -> str:
        """Try GLM-5 first, fallback to Mercury-2 if it fails."""
        import json as _json

        # Try GLM-5 first
        result = self._call_api(
            self.api_url, self.api_key, self.model,
            system, user, max_tokens
        )
        if result is not None:
            return result

        # Fallback to Mercury-2
        result = self._call_api(
            self.fallback_url, self.fallback_key, self.fallback_model,
            system, user, max_tokens
        )
        if result is not None:
            return result

        # Both failed - return None for local fallback
        return None

    def _call_api(self, url: str, api_key: str, model: str,
                  system: str, user: str, max_tokens: int) -> str:
        """Make a single API call. Returns None on failure."""
        import json as _json
        payload = _json.dumps({
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3,
        })

        try:
            result = subprocess.run(
                [
                    "curl", "-s", "--max-time", "15", "--connect-timeout", "5",
                    "-X", "POST", url,
                    "-H", "Content-Type: application/json",
                    "-H", f"Authorization: Bearer {api_key}",
                    "-d", payload,
                ],
                capture_output=True, text=True, timeout=20
            )

            if result.returncode != 0 or not result.stdout.strip():
                return None

            response = _json.loads(result.stdout)

            if "choices" in response and response["choices"]:
                content = response["choices"][0]["message"]["content"]
                return content if content else None
            else:
                return None

        except (subprocess.TimeoutExpired, _json.JSONDecodeError, Exception):
            return None

    def think(self, situation: str, context: str = "") -> str:
        """Deep chain-of-thought reasoning. GLM-5 → Mercury-2 → local."""
        system = """You are JARVIS's reasoning brain. Think step by step.
        
Analyze the situation and provide:
1. UNDERSTANDING: What is actually being asked?
2. ASSESSMENT: What tools/capabilities are available?
3. PLAN: Step-by-step action plan (numbered)
4. RISKS: What could go wrong?
5. ALTERNATIVES: Backup approaches if plan fails
6. CONFIDENCE: How confident are you? (1-10)

Be specific and actionable. Not vague advice."""

        user = f"Situation: {situation}\n\nContext: {context}" if context else situation
        result = self._call(system, user, max_tokens=1024)

        if result is None:
            return self._local_think(situation)
        return f"[Brain]\n{result}"

    def _local_think(self, situation: str) -> str:
        """Fast local reasoning when GLM-5 is unavailable."""
        lines = [
            f"[Local Reasoning] {situation}\n",
            "1. UNDERSTANDING: Breaking down the request...",
            "2. ASSESSMENT: Checking available tools and skills...",
            "3. PLAN:",
            "   - Identify the core task",
            "   - Find relevant tools/skills",
            "   - Execute step by step",
            "   - Verify results",
            "   - Report back",
            "4. RISKS: Command failure, missing dependencies, wrong paths",
            "5. ALTERNATIVES: Try different tools, ask user for clarification",
            "6. CONFIDENCE: 7/10 (local reasoning, GLM-5 unavailable)",
        ]
        return "\n".join(lines)

    def plan_task(self, goal: str, available_tools: list = None) -> list:
        """Generate a multi-step plan as structured JSON."""
        system = """You are a task planner. Break complex tasks into executable steps.

Return a JSON array of steps. Each step:
{
    "step": 1,
    "description": "What to do",
    "command": "exact command to run (if applicable)",
    "skill": "skill name to use (if applicable)",
    "check": "how to verify this step worked",
    "fallback": "what to do if this fails"
}

Only return valid JSON. No explanation."""

        tools_str = f"\nAvailable tools: {json.dumps(available_tools)}" if available_tools else ""
        user = f"Goal: {goal}{tools_str}"

        result = self._call(system, user, max_tokens=3000)

        try:
            if "```" in result:
                json_part = result.split("```")[1]
                if json_part.startswith("json"):
                    json_part = json_part[4:]
                return json.loads(json_part)
            return json.loads(result)
        except json.JSONDecodeError:
            return [{"step": 1, "description": result, "command": None}]

    def generate_skill(self, name: str, description: str, requirements: str) -> dict:
        """Generate a complete skill (handler.py + SKILL.md)."""
        system = """You are a Python developer. Generate a complete skill for JARVIS.

Return a JSON object:
{
    "handler_code": "complete Python handler.py code",
    "skill_md": "complete SKILL.md content with YAML frontmatter",
    "commands": ["list of available commands"]
}

Requirements:
- Handler must have if __name__ == "__main__" block
- Must handle errors gracefully
- Must use subprocess for shell commands
- Must have a run() helper function
- Commands should be accessible via CLI args

Only return valid JSON."""

        user = f"Skill name: {name}\nDescription: {description}\nRequirements: {requirements}"
        result = self._call(system, user, max_tokens=4000)

        try:
            if "```" in result:
                json_part = result.split("```")[1]
                if json_part.startswith("json"):
                    json_part = json_part[4:]
                return json.loads(json_part)
            return json.loads(result)
        except json.JSONDecodeError:
            return {"error": "Failed to parse GLM-5 response", "raw": result[:500]}

    def diagnose_error(self, command: str, error: str, attempts: list = None) -> str:
        """Diagnose why a command failed. Fast fallback on timeout."""
        system = """You are a Linux system diagnostician. Analyze errors and provide fixes.

Return:
1. ROOT_CAUSE: What actually went wrong
2. FIX: Exact command(s) to fix it
3. PREVENTION: How to prevent this in the future
4. ALTERNATIVE: Different approach if fix doesn't work

Be specific. Provide exact commands."""

        user = f"Command: {command}\nError: {error}"
        if attempts:
            user += f"\nPrevious attempts: {json.dumps(attempts)}"

        result = self._call(system, user)
        if result is None:
            return self._local_diagnose(command, error)
        return f"[GLM-5 Diagnosis]\n{result}"

    def _local_diagnose(self, command: str, error: str) -> str:
        """Fast local diagnosis."""
        lines = [f"[Local Diagnosis] Command: {command}\n"]
        if "command not found" in error.lower():
            cmd = command.split()[0]
            lines.append(f"ROOT_CAUSE: '{cmd}' is not installed")
            lines.append(f"FIX: sudo apt-get install -y {cmd}")
        elif "permission denied" in error.lower():
            lines.append("ROOT_CAUSE: Insufficient permissions")
            lines.append(f"FIX: sudo {command}")
        elif "no such file" in error.lower():
            lines.append("ROOT_CAUSE: File or directory doesn't exist")
            lines.append("FIX: Check path with 'ls' command")
        elif "connection refused" in error.lower():
            lines.append("ROOT_CAUSE: Service not running or port closed")
            lines.append("FIX: Check service status with systemctl")
        else:
            lines.append(f"ROOT_CAUSE: Unknown - {error[:100]}")
            lines.append("FIX: Try alternative approach or check logs")
        return "\n".join(lines)

    def analyze_gap(self, pattern: str, occurrences: int, examples: list) -> dict:
        """Analyze a recurring failure pattern and generate a solution."""
        system = """You are a system analyst. Analyze recurring failures and generate solutions.

Return a JSON object:
{
    "root_cause": "why this keeps happening",
    "solution_type": "skill|command|config|install",
    "solution": {
        "name": "suggested skill/command name",
        "description": "what it does",
        "commands": [{"name": "cmd", "desc": "...", "shell": "actual command"}]
    },
    "prevention": "how to prevent in future"
}

Only return valid JSON."""

        user = f"Pattern: {pattern}\nOccurrences: {occurrences}\nExamples: {json.dumps(examples[:3])}"
        result = self._call(system, user, max_tokens=3000)

        try:
            if "```" in result:
                json_part = result.split("```")[1]
                if json_part.startswith("json"):
                    json_part = json_part[4:]
                return json.loads(json_part)
            return json.loads(result)
        except json.JSONDecodeError:
            return {"root_cause": result[:300], "solution_type": "unknown"}

    def reflect(self, action: str, result: str, expected: str = "") -> str:
        """Deep reflection on an action's outcome."""
        system = """You are a learning agent. Reflect on what happened and extract lessons.

Return:
1. ANALYSIS: What happened and why
2. SUCCESS: Was this successful? (true/false)
3. LEARNING: What was learned
4. IMPROVEMENT: How to do better next time
5. PATTERN: Does this match a known pattern?"""

        user = f"Action: {action}\nResult: {result}"
        if expected:
            user += f"\nExpected: {expected}"

        return self._call(system, user)


# Global instance
brain = ReasoningBrain()
