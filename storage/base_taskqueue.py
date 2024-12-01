from abc import ABC, abstractmethod
from typing import Any


class TaskQueue(ABC):
    """Abstract base class for task queue"""

    @abstractmethod
    def push(self, workflow_id: str, step_name: str, params: dict[str, Any]) -> None:
        """Push a task to the queue"""
        pass

    @abstractmethod
    def pop(self) -> tuple[str, str, dict[str, Any]] | None:
        """Pop next task from the queue. Returns (workflow_id, step_name, params)"""
        pass

    @abstractmethod
    def is_empty(self) -> bool:
        """Check if queue is empty"""
        pass
