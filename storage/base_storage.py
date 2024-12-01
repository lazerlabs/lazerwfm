from abc import ABC, abstractmethod
from collections.abc import Set
from datetime import datetime

from ..workflow import Workflow


class WorkflowStorage(ABC):
    """Abstract base class for workflow storage"""

    @abstractmethod
    def add_workflow(self, workflow: Workflow) -> None:
        """Add a workflow to storage"""
        pass

    @abstractmethod
    def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Get a workflow by ID from either warm or cold storage"""
        pass

    @abstractmethod
    def move_to_cold_storage(self, workflow_id: str) -> None:
        """Move a workflow from warm to cold storage"""
        pass

    @abstractmethod
    def cleanup_cold_storage(self, before: datetime) -> None:
        """Remove workflows from cold storage older than the specified date"""
        pass

    @abstractmethod
    def get_active_workflows(self) -> Set[str]:
        """Get IDs of all workflows in warm storage"""
        pass
