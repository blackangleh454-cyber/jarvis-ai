import os
import re
import asyncio
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

from livekit.agents import function_tool, RunContext


@dataclass
class SkillInfo:
    name: str
    description: str
    instructions: str
    permissions: list = field(default_factory=list)
    keywords: list = field(default_factory=list)
    handler_path: Optional[str] = None
    handler_type: Optional[str] = None
    skill_dir: str = ""


class SkillManager:
    def __init__(self, skills_dir: str = "skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: dict[str, SkillInfo] = {}

    def discover(self):
        """Scan skills/ folder, read SKILL.md files, build skill registry."""
        self.skills.clear()

        if not self.skills_dir.exists():
            os.makedirs(self.skills_dir, exist_ok=True)
            return

        for skill_folder in sorted(self.skills_dir.iterdir()):
            if not skill_folder.is_dir():
                continue

            skill_md = skill_folder / "SKILL.md"
            if not skill_md.exists():
                continue

            skill = self._parse_skill(skill_folder, skill_md)
            if skill:
                self.skills[skill.name] = skill

    def _parse_skill(self, skill_folder: Path, skill_md: Path) -> Optional[SkillInfo]:
        """Parse a SKILL.md file with YAML frontmatter."""
        content = skill_md.read_text(encoding="utf-8")

        # Parse YAML frontmatter between --- delimiters
        frontmatter = {}
        body = content

        match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)", content, re.DOTALL)
        if match:
            frontmatter_raw = match.group(1)
            body = match.group(2)
            frontmatter = self._parse_frontmatter(frontmatter_raw)

        name = frontmatter.get("name", skill_folder.name)
        description = frontmatter.get("description", "No description")

        # Detect handler files
        handler_path = None
        handler_type = None
        for fname in ["handler.py", "handler.sh", "run.py", "run.sh"]:
            fpath = skill_folder / fname
            if fpath.exists():
                handler_path = str(fpath)
                handler_type = "python" if fname.endswith(".py") else "shell"
                break

        # Extract keywords from triggers
        keywords = []
        triggers = frontmatter.get("triggers", {})
        if isinstance(triggers, dict):
            keywords = triggers.get("keywords", [])

        # Extract permissions
        permissions = frontmatter.get("permissions", [])
        if isinstance(permissions, str):
            permissions = [permissions]

        return SkillInfo(
            name=name,
            description=description,
            instructions=body.strip(),
            permissions=permissions,
            keywords=keywords,
            handler_path=handler_path,
            handler_type=handler_type,
            skill_dir=str(skill_folder),
        )

    def _parse_frontmatter(self, raw: str) -> dict:
        """Simple YAML-like frontmatter parser (no pyyaml dependency)."""
        result = {}

        # Try to handle JSON-in-YAML metadata blocks
        # Remove metadata: { ... } blocks for simpler parsing
        raw = re.sub(r"metadata:\s*\{[^}]*\}", "", raw)

        for line in raw.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Handle key: value
            if ":" in line:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip().strip('"').strip("'")

                # Handle list items: key: [item1, item2]
                if value.startswith("[") and value.endswith("]"):
                    items = [v.strip().strip('"').strip("'") for v in value[1:-1].split(",")]
                    result[key] = [i for i in items if i]
                elif value:
                    result[key] = value
                else:
                    result[key] = {}

        return result

    def get_system_prompt(self) -> str:
        """Return only skill names + short descriptions (not full SKILL.md)."""
        if not self.skills:
            return ""

        sections = ["## Available Skills\n"]
        sections.append("Use load_skill(name) to get full instructions for a skill.\n")

        for name, skill in self.skills.items():
            desc = skill.description[:100]
            kw = f" [{', '.join(skill.keywords[:3])}]" if skill.keywords else ""
            sections.append(f"- **{name}**: {desc}{kw}")

        return "\n".join(sections)

    def get_skill_details(self, skill_name: str) -> str:
        """Return full instructions for a skill with real paths and dependency check."""
        skill = self.skills.get(skill_name)
        if not skill:
            return f"Skill '{skill_name}' not found. Available: {', '.join(self.skills.keys())}"

        parts = [f"# {skill_name}", "", skill.instructions, ""]

        # Add real file paths
        parts.append("## Files")
        parts.append(f"Skill directory: `{skill.skill_dir}`")
        if skill.handler_path:
            parts.append(f"Handler: `{skill.handler_path}`")

        # List all files in skill directory
        skill_path = Path(skill.skill_dir)
        if skill_path.exists():
            files = []
            for f in sorted(skill_path.rglob("*")):
                if f.is_file() and f.name != "_meta.json":
                    rel = f.relative_to(skill_path)
                    files.append(f"- `{rel}`")
            if files:
                parts.append("\n### Available files:")
                parts.extend(files)

        # Check dependencies
        parts.append("\n## Dependency Check")
        parts.append("Run these commands to check what's installed:")

        # Extract command references from skill instructions
        import re
        code_blocks = re.findall(r'```(?:bash|sh)?\n(.*?)```', skill.instructions, re.DOTALL)
        commands_mentioned = set()
        for block in code_blocks:
            for line in block.split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    cmd = line.split()[0].split('|')[0].strip()
                    if cmd and len(cmd) < 30:
                        commands_mentioned.add(cmd)

        for cmd in sorted(commands_mentioned):
            parts.append(f"- `which {cmd}` or `command -v {cmd}`")

        return "\n".join(parts)

    def get_tools(self) -> list:
        """Build LiveKit function_tool objects for skills that have handlers."""
        tools = []

        for name, skill in self.skills.items():
            if skill.handler_path:
                tool = self._create_tool(skill)
                tools.append(tool)

        return tools

    def _create_tool(self, skill: SkillInfo):
        """Create a function_tool for a skill with a handler."""
        handler_path = skill.handler_path
        handler_type = skill.handler_type
        skill_name = skill.name
        skill_desc = skill.description

        async def run_handler(raw_arguments: dict, context: RunContext) -> str:
            """Execute the skill handler with given arguments."""
            command = raw_arguments.get("command", "")
            return await self._execute_handler(
                handler_path, handler_type, command
            )

        # Set function metadata
        run_handler.__name__ = f"skill_{skill_name}"
        run_handler.__qualname__ = f"skill_{skill_name}"
        run_handler.__doc__ = f"{skill_desc}. Pass a 'command' argument with the specific subcommand."

        return function_tool(
            run_handler,
            name=f"skill_{skill_name}",
            description=skill_desc,
        )

    async def _execute_handler(
        self, handler_path: str, handler_type: str, command: str
    ) -> str:
        """Run a skill handler script."""
        try:
            if handler_type == "python":
                cmd = ["python", handler_path, command] if command else ["python", handler_path]
            else:
                cmd = ["bash", handler_path, command] if command else ["bash", handler_path]

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                return stdout.decode().strip() or "Command executed successfully."
            else:
                return f"Error: {stderr.decode().strip()}"

        except Exception as e:
            return f"Failed to run skill handler: {str(e)}"

    def install_skill(self, source_path: str) -> str:
        """Copy a skill folder into skills/ directory."""
        source = Path(source_path)
        if not source.exists():
            return f"Source not found: {source_path}"

        # Find SKILL.md to get the skill name
        skill_md = source / "SKILL.md"
        if not skill_md.exists():
            return "No SKILL.md found in source"

        content = skill_md.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        name = source.name
        if match:
            fm = self._parse_frontmatter(match.group(1))
            name = fm.get("name", source.name)

        dest = self.skills_dir / name
        if dest.exists():
            import shutil
            shutil.rmtree(dest)

        import shutil
        shutil.copytree(source, dest)

        self.discover()
        return f"Skill '{name}' installed successfully."
