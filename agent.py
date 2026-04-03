import os
import json
import asyncio
import time
from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool, RunContext
from livekit.agents import llm
from livekit.plugins import google, noise_cancellation

from skill_manager import SkillManager
from memory import JarvisMemory
from jarvis_prompts import IDENTITY, INSTRUCTIONS, REPLY_PROMPT, MEMORY_INSTRUCTIONS
from autonomous_engine import engine as auto_engine
from confirmation import confirm
from sub_agents import orchestrator
from intelligence import think_tool, skill_builder, self_modifier, loop_engine, gap_detector
from reasoning_brain import brain as glm_brain

# NEW: Additional JARVIS Systems
try:
    from infinite_memory import infinite_memory, remember as inf_remember
    INFINITE_MEMORY_AVAILABLE = True
except ImportError:
    INFINITE_MEMORY_AVAILABLE = False
    inf_remember = None

try:
    from jarvis_vision import jarvis_eyes
    JARVIS_EYES_AVAILABLE = True
except ImportError:
    JARVIS_EYES_AVAILABLE = False
    jarvis_eyes = None

try:
    from self_healer import self_healer
    SELF_HEALER_AVAILABLE = True
except ImportError:
    SELF_HEALER_AVAILABLE = False
    self_healer = None

try:
    from os_specialist import os_specialist
    OS_SPECIALIST_AVAILABLE = True
except ImportError:
    OS_SPECIALIST_AVAILABLE = False
    os_specialist = None

try:
    from sudo_manager import sudo_manager
    SUDO_MANAGER_AVAILABLE = True
except ImportError:
    SUDO_MANAGER_AVAILABLE = False
    sudo_manager = None

try:
    from desktop_capture import JarvisVision as DesktopVision
    DESKTOP_VISION_AVAILABLE = True
except ImportError:
    DESKTOP_VISION_AVAILABLE = False
    DesktopVision = None

load_dotenv()

# Initialize systems
BASE_DIR = os.path.dirname(__file__)
skill_mgr = SkillManager(skills_dir=os.path.join(BASE_DIR, "skills"))
skill_mgr.discover()

memory = JarvisMemory(memory_dir=os.path.join(BASE_DIR, "memory"))

# Turn counter for periodic auto-actions
_turn_counter = 0

# Pre-warm GLM-5 in background (non-blocking)
def _prewarm_glm5():
    """Warm up GLM-5 Modal endpoint in background."""
    try:
        glm_brain.think("warmup")
    except Exception:
        pass

import threading
threading.Thread(target=_prewarm_glm5, daemon=True).start()

# ─────────────────────────────────────────
# INIT ALL JARVIS SYSTEMS
# ─────────────────────────────────────────

def _init_all_systems():
    """Initialize all JARVIS subsystems on startup."""
    print("\n" + "="*50)
    print("🤖 INITIALIZING ALL JARVIS SYSTEMS...")
    print("="*50 + "\n")
    # Initialize Infinite Memory
    if INFINITE_MEMORY_AVAILABLE:
        try:
            print("✓ Infinite Memory System")
        except Exception as e:
            print(f"✗ Infinite Memory: {e}")
    
    # DON'T auto-enable camera on startup - only enable when user asks
    # (Camera privacy - don't start automatically)
    
    # Initialize OS Specialist
    if OS_SPECIALIST_AVAILABLE:
        try:
            os_info = os_specialist.get_os_info()
            print(f"✓ OS Specialist ({os_info.get('distro', 'unknown')})")
        except Exception as e:
            print(f"✗ OS Specialist: {e}")
    
    # Initialize Self-Healer
    if SELF_HEALER_AVAILABLE:
        try:
            self_healer.auto_repair = True
            print("✓ Self-Healer (Auto-repair)")
        except Exception as e:
            print(f"✗ Self-Healer: {e}")
    
    # Initialize Sudo Manager - authenticate once at startup
    if SUDO_MANAGER_AVAILABLE:
        try:
            sudo_manager.authenticate()
            print("✓ Sudo Manager (Elevated commands)")
        except Exception as e:
            print(f"✗ Sudo Manager: {e}")
    
    # Initialize Autonomous Engine (SILENT MODE - no popups)
    try:
        if not auto_engine.running:
            # Set to silent mode - no auto-remediation that causes popups
            auto_engine.autonomous_mode = False  # Disable auto-remediation
            # Don't start background monitoring that triggers sudo commands
            # auto_engine.start(60)  # Commented out to avoid sudo popups
        print("✓ Autonomous Engine (Background monitoring - passive mode)")
    except Exception as e:
        print(f"✗ Autonomous Engine: {e}")
    
    print("\n" + "="*50)
    print("✅ ALL SYSTEMS INITIALIZED!")
    print("="*50 + "\n")

# Global desktop vision instance
_desktop_vision = None

# Run initialization
_init_all_systems()

# Build system prompt (updated each turn)
def build_system_prompt():
    return "\n\n".join([
        IDENTITY,
        INSTRUCTIONS,
        MEMORY_INSTRUCTIONS,
        memory.get_memory_context(),
        skill_mgr.get_system_prompt(),
    ])


# ─────────────────────────────────────────
# TOOLS
# ─────────────────────────────────────────

@function_tool()
async def run_shell_command(context: RunContext, command: str) -> str:
    """Run a Linux shell command. Auto-retries on failure, learns from errors.
    Auto-decomposes multi-step tasks. Bypasses confirmation for trusted commands.
    Args:
        command: The shell command to execute.
    """
    # Auto-detect multi-step tasks
    multi_indicators = [" && ", " || ", " | ", ";\n", "\n&&", "\n;"]
    is_multi = any(ind in command for ind in multi_indicators)
    
    # Check if command needs decomposition
    steps = []
    if is_multi and len(command) > 200:
        parts = command.replace(" && ", ";;;").replace(" || ", ";;;").replace(" | ", ";;;").split(";;;")
        for i, part in enumerate(parts):
            if part.strip():
                steps.append({"description": f"Step {i+1}", "command": part.strip()})
    
    # Auto-decompose if 3+ steps detected
    if len(steps) >= 3:
        try:
            task = orchestrator.decompose(command, steps)
            task_result = await orchestrator.execute(task.task_id)
            return orchestrator.get_status(task.task_id)
        except Exception:
            pass  # Fall through to direct execution
    
    # ===== SUDO PASSWORD CACHING =====
    # Use cached sudo session to avoid repeated password prompts
    SUDO_PASS = "ok"
    needs_sudo = "sudo" in command.lower()
    
    if needs_sudo:
        # Remove explicit sudo and use -S with password
        clean_cmd = command.replace("sudo ", "").replace("sudo", "")
        command = f"echo '{SUDO_PASS}' | sudo -S {clean_cmd}"
    # ===== END SUDO HANDLING =====

    # Check if trusted (skip confirmation in autonomous mode)
    is_trusted = auto_engine.autonomous_mode and auto_engine.is_trusted(command)
    
    max_retries = 2
    last_error = ""

    for attempt in range(max_retries + 1):
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                result = stdout.decode().strip() or "Command executed successfully."
                # Log success after retry
                if attempt > 0:
                    memory.log_win(f"Command succeeded on retry {attempt}: {command[:50]}")
                return result
            else:
                last_error = stderr.decode().strip() or f"Exit code {process.returncode}"

                # Auto-fix: command not found → suggest install
                if "command not found" in last_error.lower():
                    cmd_name = command.split()[0].split("|")[0].strip()
                    gap_detector.record_failure(command, last_error)
                    memory.remember_conversation("system",
                        f"Command '{cmd_name}' not found. Needs installation.")
                    return (f"Command '{cmd_name}' not found. "
                           f"Try: check_tool('{cmd_name}') then install_tool('{cmd_name}')")

                # Auto-fix: permission denied → suggest sudo
                if "permission denied" in last_error.lower() and "sudo" not in command:
                    if attempt < max_retries:
                        command = f"echo '{SUDO_PASS}' | sudo -S {command}"
                        continue

                # Record failure for gap detection
                gap_detector.record_failure(command, last_error)

                # Auto-log learning
                if attempt == max_retries:
                    memory.log_struggle(f"Command failed after {max_retries+1} attempts: {command[:50]} - {last_error[:100]}")

        except Exception as e:
            last_error = str(e)
            gap_detector.record_failure(command, last_error)

        # Wait before retry
        if attempt < max_retries:
            await asyncio.sleep(1)

    return f"Failed after {max_retries+1} attempts: {last_error}"


@function_tool()
async def remember(context: RunContext, category: str, key: str, value: str) -> str:
    """Save a fact or preference to long-term memory.
    Args:
        category: Category like 'user', 'preference', 'project', 'system'.
        key: The fact name (e.g. 'name', 'language', 'favorite_editor').
        value: The fact value (e.g. 'Mirza', 'Python', 'VS Code').
    """
    memory.remember_fact(category, key, value)
    return f"Remembered: {category}/{key} = {value}"


@function_tool()
async def recall(context: RunContext, query: str) -> str:
    """Search memory for past conversations, facts, or preferences.
    Args:
        query: What to search for (e.g. 'user name', 'last project', 'wifi password').
    """
    facts = memory.recall_facts(query=query, limit=5)
    conversations = memory.recall_conversations(query=query, limit=5)

    results = []
    if facts:
        results.append("## Facts Found")
        for f in facts:
            results.append(f"- {f['category']}/{f['key']}: {f['value']}")

    if conversations:
        results.append("\n## Past Conversations")
        for c in conversations:
            role = "User" if c["role"] == "user" else "JARVIS"
            results.append(f"- [{role}]: {c['content'][:150]}")

    if not results:
        return f"No memory found for: {query}"

    return "\n".join(results)


@function_tool()
async def add_task(context: RunContext, task: str) -> str:
    """Add an active task to track.
    Args:
        task: Description of the task to track.
    """
    memory.add_task(task)
    return f"Task added: {task}"


@function_tool()
async def complete_task(context: RunContext, task: str) -> str:
    """Mark a task as completed.
    Args:
        task: Description of the task to mark complete.
    """
    memory.complete_task(task)
    return f"Task completed: {task}"


@function_tool()
async def load_skill(context: RunContext, name: str) -> str:
    """Load full instructions for a skill by name. Use when you need detailed commands.
    Args:
        name: Skill name (e.g. 'linux-desktop', 'clawstats', 'ping').
    """
    return skill_mgr.get_skill_details(name)


@function_tool()
async def list_skills(context: RunContext) -> str:
    """List all available skills with descriptions."""
    lines = []
    for name, skill in skill_mgr.skills.items():
        lines.append(f"- {name}: {skill.description[:80]}")
    return "\n".join(lines)


@function_tool()
async def check_tool(context: RunContext, command: str) -> str:
    """Check if a command/tool is installed on the system.
    Args:
        command: The command to check (e.g. 'nmap', 'x', 'syscheck').
    """
    import asyncio
    process = await asyncio.create_subprocess_exec(
        "which", command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode == 0:
        return f"Found: {stdout.decode().strip()}"
    else:
        return f"'{command}' is NOT installed. Use install_tool to install it."


@function_tool()
async def install_tool(context: RunContext, package: str) -> str:
    """Install a package using apt (Debian/Ubuntu). Use check_tool first.
    Args:
        package: Package name to install (e.g. 'nmap', 'xclip', 'htop').
    """
    import asyncio
    process = await asyncio.create_subprocess_shell(
        f"echo 'ok' | sudo -S apt-get install -y {package}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=120)
        if process.returncode == 0:
            return f"Installed: {package}\n{stdout.decode().strip()}"
        else:
            return f"Failed to install {package}: {stderr.decode().strip()}"
    except asyncio.TimeoutError:
        process.kill()
        return f"Install timed out. Run manually: sudo apt-get install -y {package}"


@function_tool()
async def log_learning(context: RunContext, entry_type: str, summary: str,
                       details: str, priority: str = "medium") -> str:
    """Log a learning, error, or feature request for self-improvement.
    Use when: (1) a command fails, (2) user corrects you, (3) you discover a better way,
    (4) user wants a missing feature, (5) you learn something new.
    Args:
        entry_type: Type of entry: 'learning', 'error', or 'feature'.
        summary: One-line description of what was learned/failed/requested.
        details: Full context: what happened, what was wrong, what's correct.
        priority: Priority level: 'low', 'medium', 'high', 'critical'.
    """
    from datetime import datetime
    import os

    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.isoformat()
    learnings_dir = os.path.join(BASE_DIR, ".learnings")

    # Generate ID
    prefix = {"learning": "LRN", "error": "ERR", "feature": "FEAT"}
    pfx = prefix.get(entry_type, "LRN")
    entry_id = f"{pfx}-{date_str}-{now.strftime('%H%M%S')}"

    # Build entry
    entry = f"""
## [{entry_id}] {entry_type}

**Logged**: {time_str}
**Priority**: {priority}
**Status**: pending

### Summary
{summary}

### Details
{details}

---
"""

    # Write to appropriate file
    files = {
        "learning": "LEARNINGS.md",
        "error": "ERRORS.md",
        "feature": "FEATURE_REQUESTS.md",
    }
    filename = files.get(entry_type, "LEARNINGS.md")
    filepath = os.path.join(learnings_dir, filename)

    with open(filepath, "a", encoding="utf-8") as f:
        f.write(entry)

    # Also save to memory for searchability
    memory.remember_fact("learning", entry_id, f"{summary} | {details[:100]}")

    return f"Logged {entry_type} [{entry_id}]: {summary}"


@function_tool()
async def web_search(context: RunContext, query: str, max_results: int = 5) -> str:
    """Search the web using DuckDuckGo. Use for current info, news, or anything online.
    Args:
        query: Search query (e.g. 'Python tutorials', 'latest AI news 2026').
        max_results: Number of results to return (default 5, max 10).
    """
    from ddgs import DDGS
    try:
        max_results = min(max_results, 10)
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                results.append(f"**{r['title']}**\n{r['body']}\n{r['href']}\n")

        if not results:
            return f"No results found for: {query}"

        return f"## Search Results for: {query}\n\n" + "\n".join(results)
    except Exception as e:
        return f"Search failed: {str(e)}"


@function_tool()
async def web_search_news(context: RunContext, query: str, max_results: int = 5) -> str:
    """Search for recent news using DuckDuckGo.
    Args:
        query: News search query (e.g. 'AI news', 'Linux updates').
        max_results: Number of results to return (default 5, max 10).
    """
    from ddgs import DDGS
    try:
        max_results = min(max_results, 10)
        results = []
        with DDGS() as ddgs:
            for r in ddgs.news(query, max_results=max_results):
                results.append(f"**{r['title']}**\n{r['body']}\n{r['url']} ({r.get('date', '')})\n")

        if not results:
            return f"No news found for: {query}"

        return f"## News Results for: {query}\n\n" + "\n".join(results)
    except Exception as e:
        return f"News search failed: {str(e)}"


# ─────────────────────────────────────────
# AUTONOMOUS ENGINE TOOLS
# ─────────────────────────────────────────

@function_tool()
async def start_monitoring(context: RunContext, interval: int = 30) -> str:
    """Start autonomous system monitoring in background.
    Args:
        interval: Check interval in seconds (default 30).
    """
    if auto_engine.running:
        return "Monitoring already running."
    asyncio.create_task(auto_engine.start(interval))
    return f"Monitoring started (interval: {interval}s). Checking CPU, memory, disk, temp, services, zombies."


@function_tool()
async def stop_monitoring(context: RunContext) -> str:
    """Stop autonomous system monitoring."""
    auto_engine.stop()
    return "Monitoring stopped."


@function_tool()
async def check_alerts(context: RunContext) -> str:
    """Check current system alerts and health status."""
    return auto_engine.get_summary()


@function_tool()
async def analyze_patterns(context: RunContext) -> str:
    """Analyze historical system patterns to predict issues."""
    return json.dumps(auto_engine.get_pattern_analysis(), indent=2)


@function_tool()
async def set_autonomous_mode(context: RunContext, enabled: bool) -> str:
    """Enable or disable autonomous mode (auto-remediation).
    Args:
        enabled: True to enable, False to disable.
    """
    return auto_engine.set_autonomous_mode(enabled)


@function_tool()
async def add_trusted(context: RunContext, pattern: str) -> str:
    """Add command pattern to trusted list (auto-execute without confirmation).
    Args:
        pattern: Command pattern to trust (e.g., 'systemctl restart').
    """
    return auto_engine.add_trusted_command(pattern)


@function_tool()
async def remove_trusted(context: RunContext, pattern: str) -> str:
    """Remove command pattern from trusted list.
    Args:
        pattern: Command pattern to remove.
    """
    return auto_engine.remove_trusted_command(pattern)


# ─────────────────────────────────────────
# CONFIRMATION TOOLS
# ─────────────────────────────────────────

@function_tool()
async def classify_command(context: RunContext, command: str) -> str:
    """Check risk level of a command before running it.
    Args:
        command: The command to classify.
    """
    level, reason = confirm.classify(command)
    return f"Risk: {level.value} | {reason}"


@function_tool()
async def approve_action(context: RunContext, action_id: str) -> str:
    """Approve a pending risky action.
    Args:
        action_id: The action ID to approve.
    """
    result = confirm.approve(action_id)
    return str(result)


@function_tool()
async def reject_action(context: RunContext, action_id: str) -> str:
    """Reject/cancel a pending risky action.
    Args:
        action_id: The action ID to reject.
    """
    result = confirm.reject(action_id)
    return str(result)


@function_tool()
async def pending_approvals(context: RunContext) -> str:
    """List all actions waiting for approval."""
    pending = confirm.get_pending()
    if not pending:
        return "No pending approvals."
    lines = []
    for p in pending:
        lines.append(f"[{p['id']}] {p['risk'].upper()}: {p['command']}")
    return "\n".join(lines)


# ─────────────────────────────────────────
# SUB-AGENT TOOLS
# ─────────────────────────────────────────

@function_tool()
async def decompose_task(context: RunContext, goal: str, steps: str) -> str:
    """Break a complex task into sub-tasks for parallel execution.
    Args:
        goal: What you want to achieve.
        steps: JSON array of steps. Each step: {"description": "...", "command": "..."}.
    """
    import json
    try:
        step_list = json.loads(steps)
        task = orchestrator.decompose(goal, step_list)
        return orchestrator.get_status(task.task_id)
    except json.JSONDecodeError:
        return "Invalid steps format. Use JSON: [{\"description\": \"...\", \"command\": \"...\"}]"


@function_tool()
async def execute_task(context: RunContext, task_id: str) -> str:
    """Execute a decomposed task with parallel sub-agents.
    Args:
        task_id: The task ID from decompose_task.
    """
    task = await orchestrator.execute(task_id)
    return orchestrator.get_status(task_id)


@function_tool()
async def task_status(context: RunContext, task_id: str) -> str:
    """Check status of a running task.
    Args:
        task_id: The task ID to check.
    """
    return orchestrator.get_status(task_id)


@function_tool()
async def list_tasks(context: RunContext) -> str:
    """List all tasks (pending, running, completed)."""
    tasks = orchestrator.get_all_tasks()
    if not tasks:
        return "No tasks."
    lines = []
    for t in tasks:
        lines.append(f"[{t['id']}] {t['status']} - {t['goal']} ({t['completed']}/{t['steps']} steps)")
    return "\n".join(lines)


# ─────────────────────────────────────────
# INTELLIGENCE LAYER TOOLS
# ─────────────────────────────────────────

@function_tool()
async def think(context: RunContext, situation: str) -> str:
    """Deep reasoning about a situation. Uses GLM-5 brain for analysis.
    Args:
        situation: What you're trying to figure out.
    """
    if glm_brain.is_available():
        # Use GLM-5 for deep reasoning
        result = glm_brain.think(situation)
        return f"[GLM-5 Reasoning]\n{result}"
    else:
        # Fallback to local think tool
        result = think_tool.think(situation)
        lines = [f"Thinking about: {situation}\n"]
        for k, v in result["framework"].items():
            lines.append(f"  {k}: {v}")
        return "\n".join(lines)


@function_tool()
async def reflect(context: RunContext, action: str, result: str) -> str:
    """Reflect on an action's outcome. Learn from success or failure.
    Args:
        action: What you did.
        result: What happened.
    """
    reflection = think_tool.reflect(action, result)
    lines = [f"Reflection on: {action}"]
    lines.append(f"Success: {reflection['success']}")
    lines.append(f"Analysis: {reflection['analysis']}")
    if reflection['learning']:
        lines.append(f"Learning: {reflection['learning']}")
    if reflection['next_action']:
        lines.append(f"Next: {reflection['next_action']}")
    return "\n".join(lines)


@function_tool()
async def build_skill(context: RunContext, name: str, description: str,
                      commands_json: str) -> str:
    """Create a new skill. Uses GLM-5 brain for code generation if available.
    Args:
        name: Skill name (lowercase, hyphens).
        description: What the skill does.
        commands_json: JSON array of commands. Each: {"name": "cmd", "desc": "...", "shell": "..."}.
    """
    try:
        commands = json.loads(commands_json)

        # If GLM-5 is available, use it to generate better code
        if glm_brain.is_available():
            skill_data = glm_brain.generate_skill(name, description, commands_json)
            if "error" not in skill_data and "handler_code" in skill_data:
                # Write GLM-generated code
                import os as _os
                skill_dir = _os.path.join(BASE_DIR, "skills", name)
                _os.makedirs(skill_dir, exist_ok=True)
                with open(_os.path.join(skill_dir, "handler.py"), "w") as f:
                    f.write(skill_data["handler_code"])
                with open(_os.path.join(skill_dir, "SKILL.md"), "w") as f:
                    f.write(skill_data.get("skill_md", f"---\nname: {name}\ndescription: \"{description}\"\n---"))
                _os.chmod(_os.path.join(skill_dir, "handler.py"), 0o755)
                skill_mgr.discover()
                return f"Skill '{name}' created with GLM-5 brain. Commands: {skill_data.get('commands', [])}"

        # Fallback to local skill builder
        result = skill_builder.create_skill(name, description, commands)
        return json.dumps(result, indent=2)
    except Exception as e:
        return f"Failed to build skill: {str(e)}"


@function_tool()
async def enhance_skill_tool(context: RunContext, skill_name: str,
                             commands_json: str) -> str:
    """Add new commands to an existing skill.
    Args:
        skill_name: Name of the skill to enhance.
        commands_json: JSON array of new commands.
    """
    import json as _json
    try:
        commands = _json.loads(commands_json)
        result = skill_builder.enhance_skill(skill_name, commands)
        return _json.dumps(result, indent=2)
    except Exception as e:
        return f"Failed to enhance skill: {str(e)}"


@function_tool()
async def add_behavior_rule(context: RunContext, rule: str) -> str:
    """Add a new rule to JARVIS's own behavior. Self-modification.
    Args:
        rule: The behavioral rule to add (e.g. 'Always confirm before deleting files').
    """
    result = self_modifier.add_rule(rule)
    return str(result)


@function_tool()
async def record_correction_tool(context: RunContext, wrong: str, correct: str) -> str:
    """Record a user correction. JARVIS learns from being wrong.
    Args:
        wrong: What JARVIS did/said that was wrong.
        correct: What the correct behavior should be.
    """
    result = self_modifier.record_correction(wrong, correct)
    return str(result)


@function_tool()
async def detect_gaps(context: RunContext) -> str:
    """Detect recurring failures and capability gaps. Find what's broken."""
    report = gap_detector.get_report()
    gaps = gap_detector.detect_gaps()
    if gaps:
        return report + "\n\nUse build_skill to create solutions for these gaps."
    return report


@function_tool()
async def record_failure_tool(context: RunContext, action: str, error: str) -> str:
    """Record a failure for pattern detection.
    Args:
        action: What was attempted.
        error: What went wrong.
    """
    gap_detector.record_failure(action, error)
    return f"Failure recorded: {action}"


@function_tool()
async def diagnose(context: RunContext, command: str, error: str) -> str:
    """Deep error diagnosis. Uses GLM-5 brain to analyze failures and suggest fixes.
    Args:
        command: The command that failed.
        error: The error message.
    """
    if glm_brain.is_available():
        result = glm_brain.diagnose_error(command, error)
        return f"[GLM-5 Diagnosis]\n{result}"
    else:
        return f"Diagnosis: Command '{command}' failed with: {error}\nSuggestion: Check if the tool is installed or try a different approach."


# ─────────────────────────────────────────
# NEW JARVIS SYSTEMS TOOLS
# ─────────────────────────────────────────

@function_tool()
async def infinite_remember(context: RunContext, what: str, importance: float = 5.0) -> str:
    """Remember something forever in infinite memory. JARVIS never forgets.
    Args:
        what: What to remember.
        importance: How important (0-10, default 5).
    """
    if not INFINITE_MEMORY_AVAILABLE:
        return "Infinite Memory not available."
    try:
        id_ = infinite_memory.remember_everything(what, importance=importance)
        return f"Remembered forever: {what[:50]}... (ID: {id_})"
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def infinite_recall(context: RunContext, query: str) -> str:
    """Search infinite memory for anything JARVIS has remembered.
    Args:
        query: What to search for.
    """
    if not INFINITE_MEMORY_AVAILABLE:
        return "Infinite Memory not available."
    try:
        results = infinite_memory.recall_human_style(query)
        if not results:
            return f"No memories found for: {query}"
        lines = [f"Found {len(results)} memories:"]
        for r in results[:5]:
            lines.append(f"- [{r.get('context', 'unknown')}] {r.get('memory', '')[:80]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def infinite_stats(context: RunContext) -> str:
    """Get memory statistics."""
    if not INFINITE_MEMORY_AVAILABLE:
        return "Infinite Memory not available."
    try:
        stats = infinite_memory.get_memory_stats()
        return f"Infinite Memory: {stats['total_memories']} memories stored. DB size: {stats['db_size_mb']}MB"
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def open_eyes(context: RunContext) -> str:
    """Enable JARVIS vision - let JARVIS see through the laptop camera."""
    if not JARVIS_EYES_AVAILABLE:
        return "JARVIS Eyes not available."
    try:
        import jarvis_vision
        jarvis_vision.jarvis_eyes.enable("/dev/video0")
        return "JARVIS eyes are now open. I can see!"
    except Exception as e:
        return f"Could not open eyes: {e}"

@function_tool()
async def close_eyes(context: RunContext) -> str:
    """Disable JARVIS vision."""
    if not JARVIS_EYES_AVAILABLE:
        return "JARVIS Eyes not available."
    try:
        import jarvis_vision
        jarvis_vision.jarvis_eyes.disable()
        return "JARVIS eyes are now closed."
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def what_do_you_see(context: RunContext) -> str:
    """Ask JARVIS what they see through the camera."""
    if not JARVIS_EYES_AVAILABLE:
        return "JARVIS Eyes not available."
    try:
        import jarvis_vision
        eyes = jarvis_vision.jarvis_eyes
        if not jarvis_eyes._enabled:
            return "My eyes are closed. Say 'open your eyes' to enable vision."
        return jarvis_eyes.observe()
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def anyone_home(context: RunContext) -> str:
    """Check if anyone is in front of the camera."""
    if not JARVIS_EYES_AVAILABLE:
        return "JARVIS Eyes not available."
    try:
        import jarvis_vision
        if jarvis_vision.jarvis_eyes.is_anyone_there():
            return "Yes! Someone is there!"
        return "No one is in front of me."
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def see_desktop(context: RunContext) -> str:
    """JARVIS looks at the computer screen."""
    global _desktop_vision
    if not DESKTOP_VISION_AVAILABLE:
        return "Desktop Vision not available."
    try:
        if _desktop_vision is None:
            _desktop_vision = DesktopVision()
            _desktop_vision.enable()
        return _desktop_vision.see()
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def check_system_health(context: RunContext) -> str:
    """Run comprehensive system health check using Self-Healer."""
    if not SELF_HEALER_AVAILABLE:
        return "Self-Healer not available."
    try:
        report = self_healer.get_health_report()
        score = report.get('health_score', 0)
        issues = report.get('total_issues', 0)
        return f"System Health Score: {score}/100. Issues found: {issues}"
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def auto_repair_system(context: RunContext) -> str:
    """Auto-repair any system issues."""
    if not SELF_HEALER_AVAILABLE:
        return "Self-Healer not available."
    try:
        results = self_healer.auto_repair_all()
        return f"Repaired: {results.get('repaired', 0)}. Failed: {results.get('failed', 0)}"
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def get_os_info(context: RunContext) -> str:
    """Get detailed OS information."""
    if not OS_SPECIALIST_AVAILABLE:
        return "OS Specialist not available."
    try:
        info = os_specialist.get_os_info()
        return f"OS: {info.get('distro', 'unknown')} {info.get('distro_version', '')}. Desktop: {info.get('desktop_env', 'unknown')}. Kernel: {info.get('kernel', 'unknown')[:20]}"
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def run_sudo_command(context: RunContext, command: str) -> str:
    """Execute command with sudo (elevated privileges).
    Args:
        command: The command to run with sudo.
    """
    if not SUDO_MANAGER_AVAILABLE:
        return "Sudo Manager not available."
    try:
        success, output = sudo_manager.execute(command)
        return output[:1000] if output else ("Success" if success else "Failed")
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def sudo_status(context: RunContext) -> str:
    """Check sudo authentication status."""
    if not SUDO_MANAGER_AVAILABLE:
        return "Sudo Manager not available."
    try:
        auth = sudo_manager.is_authenticated()
        return f"Sudo authenticated: {auth}"
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def check_alerts_autonomous(context: RunContext) -> str:
    """Check system alerts from autonomous monitoring."""
    try:
        return auto_engine.get_summary()
    except Exception as e:
        return f"Error: {e}"

@function_tool()
async def enable_autonomous_mode(context: RunContext, enabled: bool = True) -> str:
    """Enable or disable autonomous mode (auto-remediation).
    Args:
        enabled: True to enable, False to disable.
    """
    try:
        return auto_engine.set_autonomous_mode(enabled)
    except Exception as e:
        return f"Error: {e}"


# ─────────────────────────────────────────
# AGENT
# ─────────────────────────────────────────

class Assistant(Agent):
    def __init__(self, chat_ctx) -> None:
        all_tools = [run_shell_command, remember, recall,
                     add_task, complete_task, load_skill, list_skills,
                     check_tool, install_tool, log_learning,
                     web_search, web_search_news,
                     start_monitoring, stop_monitoring, check_alerts,
                     analyze_patterns, set_autonomous_mode, add_trusted, remove_trusted,
                     classify_command, approve_action, reject_action, pending_approvals,
                     decompose_task, execute_task, task_status, list_tasks,
                     think, reflect, build_skill, enhance_skill_tool,
                     add_behavior_rule, record_correction_tool,
                     detect_gaps, record_failure_tool, diagnose,
                     # NEW JARVIS SYSTEMS
                     infinite_remember, infinite_recall, infinite_stats,
                     open_eyes, close_eyes, what_do_you_see, anyone_home, see_desktop,
                     check_system_health, auto_repair_system, get_os_info,
                     run_sudo_command, sudo_status,
                     check_alerts_autonomous, enable_autonomous_mode] + skill_mgr.get_tools()

        super().__init__(
            chat_ctx=chat_ctx,
            instructions=build_system_prompt(),
            llm=google.beta.realtime.RealtimeModel(
                model="gemini-2.5-flash-native-audio-preview-09-2025",
                voice="Charon",
            ),
            tools=all_tools,
        )

    async def on_enter(self):
        """Called when agent starts. Track session + start monitoring."""
        memory.increment_session()
        # Auto-start autonomous monitoring in background
        if not auto_engine.running:
            asyncio.create_task(auto_engine.start(60))  # Check every 60 seconds

    async def on_user_turn_completed(
        self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage
    ):
        """Auto: check alerts, detect gaps, auto-build skills, update context."""
        global _turn_counter
        _turn_counter += 1
        user_text = new_message.text_content or ""

        if user_text.strip():
            # Auto-check for system alerts
            alerts = auto_engine.get_summary()
            if "All systems healthy" not in alerts:
                memory.remember_conversation("system", f"System alert: {alerts[:200]}")

            # Every 5 turns: auto-gap detection + auto-skill-building
            if _turn_counter % 5 == 0:
                gaps = gap_detector.detect_gaps()
                if gaps:
                    top_gap = gaps[0]
                    memory.remember_conversation("system",
                        f"Recurring issue: {top_gap['pattern']} ({top_gap['occurrences']} times)")

                    # Auto-build skill if gap has 3+ occurrences
                    if top_gap["occurrences"] >= 3:
                        skill_name = top_gap["pattern"].replace(":", "-").replace(" ", "-")[:30]
                        try:
                            # Use GLM-5 brain for better solution if available
                            if glm_brain.is_available():
                                analysis = glm_brain.analyze_gap(
                                    top_gap["pattern"],
                                    top_gap["occurrences"],
                                    top_gap.get("examples", [])
                                )
                                if "solution" in analysis and "commands" in analysis["solution"]:
                                    skill_builder.create_skill(
                                        name=f"auto-fix-{skill_name}",
                                        description=analysis.get("solution", {}).get("description", f"Auto-fix for {skill_name}"),
                                        commands=analysis["solution"]["commands"],
                                        test_commands=False,
                                    )
                                else:
                                    skill_builder.create_skill(
                                        name=f"auto-fix-{skill_name}",
                                        description=f"Auto-generated fix for: {top_gap['pattern']}",
                                        commands=[{
                                            "name": "fix",
                                            "desc": top_gap["suggestion"],
                                            "shell": top_gap["suggestion"].replace("Install: ", "").replace("Run with ", ""),
                                        }],
                                        test_commands=False,
                                    )
                            else:
                                skill_builder.create_skill(
                                    name=f"auto-fix-{skill_name}",
                                    description=f"Auto-generated fix for: {top_gap['pattern']}",
                                    commands=[{
                                        "name": "fix",
                                        "desc": top_gap["suggestion"],
                                        "shell": top_gap["suggestion"].replace("Install: ", "").replace("Run with ", ""),
                                    }],
                                    test_commands=False,
                                )
                            memory.log_win(f"Auto-built skill for: {top_gap['pattern']}")
                            skill_mgr.discover()
                        except Exception:
                            pass

            # Auto-load relevant skills based on context
            user_lower = user_text.lower()
            skill_keywords = {
                "website": "website-generator",
                "api": "api-builder", 
                "database": "database-manager",
                "docker": "docker-manager",
                "deploy": "devops-deploy",
                "test": "testing-suite",
                "cpu": "system-health",
                "process": "process-manager",
                "disk": "disk-cleaner",
                "service": "service-controller",
                "network": "network-info",
                "wifi": "wifi-manager",
                "ssh": "ssh-commander",
                "security": "system-hardening",
                "backup": "auto-backup",
                "install": "package-manager",
                "cron": "cron-manager",
                "log": "log-watcher",
                "firewall": "advanced-firewall",
                "port": "port-manager",
                "ssl": "ssl-checker",
                "privacy": "privacy-checker",
                "osint": "osint-scanner",
                "youtube": "youtube-downloader",
            }
            
            for keyword, skill_name in skill_keywords.items():
                if keyword in user_lower and skill_name in skill_mgr.skills:
                    _ = skill_mgr.get_skill_details(skill_name)
                    break

            # Update system prompt with fresh context
            await self.update_instructions(build_system_prompt())

    async def on_exit(self):
        """Called when agent shuts down. Save final state."""
        pass


# ─────────────────────────────────────────
# ENTRYPOINT
# ─────────────────────────────────────────

async def entrypoint(ctx: agents.JobContext):
    session = AgentSession()

    @session.on("conversation_item_added")
    def on_conversation_item_added(event):
        """Save both user and assistant messages to memory."""
        item = event.item
        if hasattr(item, 'role') and hasattr(item, 'text_content'):
            text = item.text_content
            if text and text.strip():
                memory.remember_conversation(item.role, text.strip())

    await session.start(
        room=ctx.room,
        agent=Assistant(chat_ctx=[]),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
