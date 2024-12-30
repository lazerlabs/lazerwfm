from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from .types import StepTransition, WorkflowStatus


class Workflow:
    """Base class for all workflows"""

    def __init__(self, name: str = "Unnamed Workflow"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.status = WorkflowStatus.PENDING
        self._result: Any = None
        self._error: Exception | None = None
        self.created_at = datetime.now()
        self.current_step_name: str | None = None

    async def start(self, **params) -> StepTransition:
        """Entry point for the workflow"""
        raise NotImplementedError("Workflows must implement start method")

    def get_result(self) -> Any:
        return self._result

    def set_result(self, result: Any):
        self._result = result

    def get_error(self) -> Exception | None:
        return self._error

    def set_error(self, error: Exception):
        self._error = error
        self.status = WorkflowStatus.FAILED

    def set_current_step(self, step_name: str):
        """Update the current step name"""
        self.current_step_name = step_name
