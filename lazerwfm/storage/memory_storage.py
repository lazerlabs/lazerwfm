from collections.abc import Set
from datetime import datetime

from ..types import WorkflowStatus
from ..workflow import Workflow
from .base_storage import WorkflowStorage


class MemoryWorkflowStorage(WorkflowStorage):
    """In-memory implementation of workflow storage"""

    def __init__(self):
        self._warm_storage: dict[str, Workflow] = {}
        self._cold_storage: dict[str, Workflow] = {}
        self._terminal_states = {
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
        }

    def add_workflow(self, workflow: Workflow) -> None:
        """Add a workflow to warm storage"""
        self._warm_storage[workflow.id] = workflow

    def get_workflow(self, workflow_id: str) -> Workflow | None:
        """Get a workflow from either warm or cold storage"""
        return self._warm_storage.get(workflow_id) or self._cold_storage.get(
            workflow_id
        )

    def move_to_cold_storage(self, workflow_id: str) -> None:
        """Move a workflow from warm to cold storage if it's in a terminal state"""
        workflow = self._warm_storage.get(workflow_id)
        if workflow and workflow.status in self._terminal_states:
            self._cold_storage[workflow_id] = workflow
            del self._warm_storage[workflow_id]

    def cleanup_cold_storage(self, before: datetime) -> None:
        """Remove workflows from cold storage older than the specified date"""
        # In this simple implementation, we don't track timestamps
        # This would be implemented in persistent storage backends
        pass

    def get_active_workflows(self) -> Set[str]:
        """Get IDs of all workflows in warm storage"""
        return set(self._warm_storage.keys())
