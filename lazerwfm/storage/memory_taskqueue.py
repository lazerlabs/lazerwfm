from collections import deque
from typing import Any

from .base_taskqueue import TaskQueue


class MemoryTaskQueue(TaskQueue):
    """In-memory implementation of task queue using deque"""

    def __init__(self):
        self._queue: deque[tuple[str, str, dict[str, Any]]] = deque()

    def push(self, workflow_id: str, step_name: str, params: dict[str, Any]) -> None:
        """Push a task to the queue"""
        self._queue.append((workflow_id, step_name, params))

    def pop(self) -> tuple[str, str, dict[str, Any]] | None:
        """Pop next task from the queue"""
        try:
            return self._queue.popleft()
        except IndexError:
            return None

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self._queue) == 0
