"""Sub-Agent System - Task decomposition and parallel execution.

Breaks complex tasks into sub-tasks, spawns workers, collects results.
"""
import asyncio
import time
import subprocess
import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class SubTask:
    task_id: str
    description: str
    command: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    dependencies: list = field(default_factory=list)


@dataclass
class ComplexTask:
    task_id: str
    goal: str
    subtasks: list[SubTask] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    summary: Optional[str] = None


class SubAgent:
    """A worker that executes sub-tasks."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.busy = False
        self.current_task: Optional[SubTask] = None

    async def execute(self, task: SubTask) -> SubTask:
        """Execute a sub-task."""
        self.busy = True
        self.current_task = task
        task.status = TaskStatus.RUNNING
        task.started_at = time.time()

        try:
            if task.command:
                process = await asyncio.create_subprocess_shell(
                    task.command,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), timeout=60
                )
                if process.returncode == 0:
                    task.result = stdout.decode().strip() or "Completed"
                    task.status = TaskStatus.COMPLETED
                else:
                    task.error = stderr.decode().strip()
                    task.status = TaskStatus.FAILED
            else:
                task.result = f"Task '{task.description}' planned (no command to execute)"
                task.status = TaskStatus.COMPLETED

        except asyncio.TimeoutError:
            task.error = "Timeout after 60s"
            task.status = TaskStatus.FAILED
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED

        task.completed_at = time.time()
        self.busy = False
        self.current_task = None
        return task


class SubAgentOrchestrator:
    """Manages task decomposition and parallel execution."""

    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.agents = [SubAgent(f"worker_{i}") for i in range(max_workers)]
        self.tasks: dict[str, ComplexTask] = {}
        self._id_counter = 0

    def decompose(self, goal: str, steps: list[dict]) -> ComplexTask:
        """Create a complex task from a goal and steps.

        steps format: [{"description": "...", "command": "..."}, ...]
        """
        self._id_counter += 1
        task_id = f"task_{self._id_counter}_{int(time.time())}"

        subtasks = []
        for i, step in enumerate(steps):
            subtasks.append(SubTask(
                task_id=f"{task_id}_step_{i}",
                description=step.get("description", f"Step {i+1}"),
                command=step.get("command"),
                dependencies=step.get("dependencies", []),
            ))

        complex_task = ComplexTask(
            task_id=task_id,
            goal=goal,
            subtasks=subtasks,
        )
        self.tasks[task_id] = complex_task
        return complex_task

    async def execute(self, task_id: str) -> ComplexTask:
        """Execute a complex task with parallel workers."""
        task = self.tasks.get(task_id)
        if not task:
            return task

        task.status = TaskStatus.RUNNING

        # Execute subtasks in dependency order
        completed_ids = set()
        remaining = list(task.subtasks)

        while remaining:
            # Find tasks whose dependencies are met
            ready = [
                st for st in remaining
                if all(dep in completed_ids for dep in st.dependencies)
            ]

            if not ready:
                # Deadlock - remaining tasks have unmet dependencies
                for st in remaining:
                    st.status = TaskStatus.FAILED
                    st.error = "Unmet dependencies"
                break

            # Find available agents
            available = [a for a in self.agents if not a.busy]
            batch = ready[:len(available)]

            if not batch:
                await asyncio.sleep(0.5)
                continue

            # Execute batch in parallel
            results = await asyncio.gather(
                *[agent.execute(st) for agent, st in zip(available, batch)]
            )

            for st in results:
                remaining.remove(st)
                if st.status == TaskStatus.COMPLETED:
                    completed_ids.add(st.task_id)

        # Generate summary
        completed = sum(1 for st in task.subtasks if st.status == TaskStatus.COMPLETED)
        failed = sum(1 for st in task.subtasks if st.status == TaskStatus.FAILED)
        task.summary = f"Goal: {task.goal}\nCompleted: {completed}/{len(task.subtasks)}, Failed: {failed}"
        task.status = TaskStatus.COMPLETED if failed == 0 else TaskStatus.FAILED

        return task

    def get_status(self, task_id: str) -> str:
        """Get human-readable task status."""
        task = self.tasks.get(task_id)
        if not task:
            return f"Task {task_id} not found"

        lines = [f"## Task: {task.goal}"]
        lines.append(f"Status: {task.status.value}\n")

        for st in task.subtasks:
            icon = {"pending": "⏳", "running": "🔄", "completed": "✅", "failed": "❌"}[st.status.value]
            lines.append(f"  {icon} {st.description}")
            if st.result and len(st.result) < 100:
                lines.append(f"     → {st.result}")
            if st.error:
                lines.append(f"     → Error: {st.error}")

        return "\n".join(lines)

    def get_all_tasks(self) -> list[dict]:
        """List all complex tasks."""
        return [
            {
                "id": t.task_id,
                "goal": t.goal,
                "status": t.status.value,
                "steps": len(t.subtasks),
                "completed": sum(1 for s in t.subtasks if s.status == TaskStatus.COMPLETED),
            }
            for t in self.tasks.values()
        ]


# Global instance
orchestrator = SubAgentOrchestrator(max_workers=4)
